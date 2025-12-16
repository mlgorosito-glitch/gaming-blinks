import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

class BlinkDetector:
    def __init__(self, serial_port="COM6", eog_channel=2):
        try:
            BoardShim.release_all_sessions()
        except Exception:
            pass

        self.params = BrainFlowInputParams()
        self.params.serial_port = serial_port
        self.board_id = BoardIds.CYTON_BOARD.value
        self.board = BoardShim(self.board_id, self.params)

        self.EOG_CH = eog_channel

        print("[BlinkDetector] Preparando sesión...")
        self.board.prepare_session()
        self.board.start_stream()

        self.fs = BoardShim.get_sampling_rate(self.board_id)
        print(f"[BlinkDetector] fs = {self.fs} Hz")

        #Filtro pasabanda
        lowcut = 0.5
        highcut = 10.0
        order = 4
        nyq = 0.5 * self.fs
        self.b, self.a = butter(order, [lowcut / nyq, highcut / nyq], btype="band")
        self.zi = lfilter_zi(self.b, self.a) * 0.0

        #Ventana para visualizacion/debug
        self.WINDOW_SEC = 6.0
        self.N_SAMPLES = int(self.WINDOW_SEC * self.fs)
        self.eog_buffer = np.zeros(self.N_SAMPLES)

        #Bloques de procesamiento
        self.BLOCK_SEC = 0.1
        self.BLOCK_SIZE = int(self.BLOCK_SEC * self.fs)

        #Umbral
        self.THRESHOLD_MV = 0.3
        self.THRESHOLD_UV = self.THRESHOLD_MV * 1000.0

        #Refractario y warmup
        self.REFRACTORY_SEC = 0.5
        self.REFRACTORY_SAMPLES = int(self.REFRACTORY_SEC * self.fs)

        self.WARMUP_SEC = 5.0
        self.WARMUP_SAMPLES = int(self.WARMUP_SEC * self.fs)

        #Contadores "reales" (en muestras procesadas)
        self.global_sample_counter = 0
        self.last_blink_sample = -10**12
        self.blink_count = 0

        #Buffer de muestras nuevas pendientes
        self.pending = np.array([], dtype=float)

    def update(self) -> bool:
        
        data = self.board.get_board_data()
        if data is None or data.size == 0:
            return False

        new_samples = data[self.EOG_CH, :].astype(float)
        if new_samples.size == 0:
            return False

        self.pending = np.concatenate([self.pending, new_samples])
        detected = False

        #Procesar todos los bloques completos disponibles
        while self.pending.size >= self.BLOCK_SIZE:
            chunk = self.pending[: self.BLOCK_SIZE]
            self.pending = self.pending[self.BLOCK_SIZE :]

            #Filtrado con estado
            filt, self.zi = lfilter(self.b, self.a, chunk, zi=self.zi)

            #Buffer rolling (6 s) para inspección
            self.eog_buffer = np.roll(self.eog_buffer, -self.BLOCK_SIZE)
            self.eog_buffer[-self.BLOCK_SIZE :] = filt

            #Deteccion por maximo absoluto del bloque
            abs_chunk = np.abs(filt)
            local_max_idx = int(np.argmax(abs_chunk))
            local_max_val = float(abs_chunk[local_max_idx])

            blink_candidate = self.global_sample_counter + local_max_idx

            #Warm-up
            if self.global_sample_counter >= self.WARMUP_SAMPLES:
                if (local_max_val > self.THRESHOLD_UV and
                    blink_candidate - self.last_blink_sample > self.REFRACTORY_SAMPLES):
                    self.last_blink_sample = blink_candidate
                    self.blink_count += 1
                    detected = True

            #Avanzar contador de muestras procesadas (real)
            self.global_sample_counter += self.BLOCK_SIZE

        return detected

    def stop(self):
        print("[BlinkDetector] Deteniendo stream...")
        self.board.stop_stream()
        self.board.release_session()
        print("[BlinkDetector] Sesión cerrada.")
