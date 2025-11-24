import io, zipfile, xml.etree.ElementTree as ET
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DART_API_KEY = os.getenv("DART_API_KEY")
CORP_URL = "https://opendart.fss.or.kr/api/corpCode.xml"

def fetch_corpcode_zip() -> bytes:
    if not DART_API_KEY:
        raise RuntimeError("DART_API_KEY is empty")
    r = requests.get(CORP_URL, params={"crtfc_key": DART_API_KEY}, timeout=90)
    r.raise_for_status() # HTTP 상태코드가 4xx/5xx면 request.HTTPError 예외를 던져서 상위에서 처리하게 함
    return r.content # 결과물: zip 바이너리

def parse_corpcode_xml(zip_bytes: bytes):
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
        xml_name = [n for n in zf.namelist() if n.lower().endswith(".xml")][0]
        xml_bytes = zf.read(xml_name)

    root = ET.fromstring(xml_bytes) # XML 파싱 -> 루트 Element
    for el in root.findall(".//list"): # 경로에 해당하는 하위 노드 리스트
        yield{
            "corp_code":    el.findtext("corp_code"),
            "name_ko":      el.findtext("corp_name"),
            "name_en":      el.findtext("corp_eng_name"),
            "stock_code":   el.findtext("stock_code"),
        }