# Çalışan bir Kaggle defterinin canlı günlüğünü okur (CLI'nin "logs" komutu çalışırken boş döner).
# Kullanım: uvx --from kaggle python canli.py <defter-adı> [saniye]
import sys, time, os
from kaggle.api.kaggle_api_extended import KaggleApi
from kagglesdk.kernels.types.kernels_api_service import ApiGetKernelSessionLogsStreamRequest
a = KaggleApi(); a.authenticate()
r = ApiGetKernelSessionLogsStreamRequest()
r.user_name = os.environ["KAGGLE_SAHIP"]; r.kernel_slug = sys.argv[1]; r.wait_for_logs_url_seconds = 20
sure = float(sys.argv[2]) if len(sys.argv) > 2 else 20
with a.build_kaggle_client() as k:
    h = k.kernels.kernels_api_client._client
    h._init_session()
    istek = h._prepare_request("kernels.KernelsApiService", "GetKernelSessionLogsStream", r)
    y = h._session.send(istek, stream=True, timeout=(20, sure))
    print("durum", y.status_code, y.headers.get("Content-Type"), flush=True)
    t0 = time.time()
    try:
        for satir in y.iter_lines(decode_unicode=True):
            if satir and "Warning" not in satir: print(satir[:400], flush=True)
            if time.time() - t0 > sure: break
    except Exception as e:
        print("bitti:", type(e).__name__)
