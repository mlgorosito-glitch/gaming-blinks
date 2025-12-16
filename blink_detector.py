import time
import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi
from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

class BlinkDetector:

    def __init__(self, serial_port="COM6", eog_channel=2):
        #Cerrar cualquier sesion previa
        try:
            BoardShim.release_all_sessions()
        except Exception:
            pass

        #Conectarse con la placa
        self.params = BrainFlowInputParams()
        self.params.serial_port = serial_port
        self.board_id = BoardIds.CYTON_BOARD.value
        self.board = BoardShim(self.board_id, self.params)

        self.EOG_CH = eog_channel

        print("[BlinkDetector] Preparando sesión...")
        self.board.prepare_session()
        self.board.start_stream()

        #Toma la frecuencia de muestreo real del aparato
        self.fs = BoardShim.get_sampling_rate(self.board_id)
        print(f"[BlinkDetector] fs = {self.fs} Hz")

        #Filtrar la señal - Matando lo que no sirve 
        lowcut = 0.5
        highcut = 10.0
        order = 4
        nyq = 0.5 * self.fs
        self.b, self.a = butter(order, [lowcut/nyq, highcut/nyq], btype='band')
        self.zi = lfilter_zi(self.b, self.a) * 0.0

        #Buffer
        self.WINDOW_SEC = 6.0
        self.N_SAMPLES = int(self.WINDOW_SEC * self.fs)
        self.eog_buffer = np.zeros(self.N_SAMPLES)

        self.BLOCK_SEC = 0.1
        self.BLOCK_SIZE = int(self.BLOCK_SEC * self.fs)

        #Umbral de detección fijo -Ajustar
        self.THRESHOLD_MV = 0.3   # mV
        self.THRESHOLD_UV = self.THRESHOLD_MV * 1000.0  # µV

        #Periodo refractario 
        self.REFRACTORY_SEC = 0.5
        self.REFRACTORY_SAMPLES = int(self.REFRACTORY_SEC * self.fs)

        #Estabilizacion de la señal
        self.WARMUP_SEC = 5.0
        self.WARMUP_SAMPLES = int(self.WARMUP_SEC * self.fs)

        self.global_sample_counter = 0
        self.last_blink_sample = -10**12
        self.blink_count = 0

    def update(self):
        """
        Devuelve:
            - True si se detectó un blink en este frame
            - False en caso contrario
        """
        data = self.board.get_current_board_data(self.BLOCK_SIZE)

        if data.shape[1] < self.BLOCK_SIZE:
            return False
        #Señal cruda en µV
        chunk = data[self.EOG_CH, :].astype(float)
        #Filtrar con estado
        filt, self.zi = lfilter(self.b, self.a, chunk, zi=self.zi)
        #Actualizar buffer circular
        self.eog_buffer = np.roll(self.eog_buffer, -self.BLOCK_SIZE)
        self.eog_buffer[-self.BLOCK_SIZE:] = filt
        #Deteccion
        abs_chunk = np.abs(filt)
        local_max_idx = int(np.argmax(abs_chunk))
        local_max_val = float(abs_chunk[local_max_idx])

        blink_candidate = self.global_sample_counter + local_max_idx

        #Warm-up (evita falsos positivos al inicio)
        if self.global_sample_counter < self.WARMUP_SAMPLES:
            self.global_sample_counter += self.BLOCK_SIZE
            return False
        #Verificar si pasa umbral + refractario
        if (local_max_val > self.THRESHOLD_UV and
            blink_candidate - self.last_blink_sample > self.REFRACTORY_SAMPLES):

            self.last_blink_sample = blink_candidate
            self.blink_count += 1
            self.global_sample_counter += self.BLOCK_SIZE
            return True  
        self.global_sample_counter += self.BLOCK_SIZE
        return False

    def stop(self):
        print("[BlinkDetector] Deteniendo stream...")
        self.board.stop_stream()
        self.board.release_session()
        print("[BlinkDetector] Sesión cerrada.")
