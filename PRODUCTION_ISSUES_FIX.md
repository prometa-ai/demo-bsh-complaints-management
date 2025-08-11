# Production Issues and Fixes

## Sorunlar

### 1. Veritabanı Başlatma Sorunu
**Problem**: Canlı ortamda uygulama başladığında veritabanı boş kalıyor ve veriler gelmiyor.

**Neden**: 
- `setup_database.py` ve `regenerate_consistent_data.py` dosyaları uygulama başlamadan çalışmıyor
- Cloud Storage'dan veritabanı indirilemiyor
- Veritabanı dosyası oluşturulamıyor

**Çözüm**:
- `startup_script.py` oluşturuldu - uygulama başlamadan önce çalışır
- Dockerfile güncellendi - startup script'i çalıştırır
- Veritabanı başlatma fonksiyonları daha güvenli hale getirildi
- Hata yönetimi iyileştirildi

### 2. TTS (Text-to-Speech) Hatası
**Problem**: 
```
talk_with_data:735 TTS Error: Speech synthesis failed: 'NoneType' object has no attribute 'audio'
```

**Neden**: 
- OpenAI client `None` olarak kalıyor
- API key doğru yüklenmiyor

**Çözüm**:
- TTS fonksiyonunda client kontrolü eklendi
- Daha iyi hata mesajları eklendi
- OpenAI client başlatma süreci iyileştirildi

### 3. Cloud Storage Bağlantı Sorunu
**Problem**: Canlı ortamda veritabanı GCS'den indirilemiyor.

**Neden**:
- GCS bucket oluşturulmamış
- İzinler eksik
- Bağlantı hataları

**Çözüm**:
- `cloud_storage_db.py` güncellendi - daha iyi hata yönetimi
- Directory oluşturma eklendi
- Fallback mekanizması iyileştirildi

## Yapılan Değişiklikler

### 1. Startup Script (`startup_script.py`)
- Uygulama başlamadan önce çalışır
- Veritabanı kurulumunu kontrol eder
- Veri yoksa örnek veri oluşturur
- OpenAI bağlantısını test eder
- Cloud Storage bağlantısını test eder

### 2. Dockerfile Güncellemesi
```dockerfile
# Run startup script first, then the application
CMD ["sh", "-c", "python startup_script.py && python -m gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 app:app"]
```

### 3. Veritabanı Bağlantı İyileştirmeleri
- `connect_to_db()` fonksiyonu güncellendi
- Daha iyi hata yönetimi eklendi
- Directory oluşturma eklendi

### 4. TTS Fonksiyonu Düzeltmesi
- Client kontrolü eklendi
- Daha açık hata mesajları

## Deployment

### Yeni Deployment Script (`deploy_production.sh`)
```bash
./deploy_production.sh
```

Bu script:
- Gerekli API'leri etkinleştirir
- GCS bucket oluşturur
- Cloud Build ile deploy eder

### Manuel Deployment
```bash
# 1. GCS bucket oluştur
gsutil mb -p demo-bsh-complaints-management -c STANDARD -l europe-west1 gs://bsh-complaints-db-bucket

# 2. Deploy et
gcloud builds submit --config cloudbuild.yaml --substitutions=_SERVICE_NAME=demo-bsh-complaints-management,_DEPLOY_REGION=europe-west1,_PLATFORM=managed,_GCP_PROJECT_ID=demo-bsh-complaints-management,_GCS_BUCKET_NAME=bsh-complaints-db-bucket,_SECRET_MANAGER_KEY=openai-api-key .
```

## Test Etme

### Health Check
```bash
curl https://prod-demo-bsh-complaints-management-685463200361.europe-west1.run.app/health
```

### Veritabanı Kontrolü
1. Uygulamaya giriş yap
2. Complaints sayfasına git
3. Verilerin yüklenip yüklenmediğini kontrol et

### TTS Test
1. Talk with Data sayfasına git
2. Bir soru sor
3. Ses çıkışının çalışıp çalışmadığını kontrol et

## Sorun Giderme

### Veritabanı Hala Boşsa
1. Cloud Run loglarını kontrol et:
```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=demo-bsh-complaints-management" --limit=50
```

2. Startup script loglarını kontrol et
3. GCS bucket'ta veritabanı dosyası var mı kontrol et

### TTS Hala Çalışmıyorsa
1. OpenAI API key'in doğru ayarlandığını kontrol et
2. Secret Manager'da key'in var olduğunu kontrol et
3. API key'in geçerli olduğunu test et

### Cloud Storage Sorunu
1. Bucket izinlerini kontrol et
2. Service account izinlerini kontrol et
3. Network bağlantısını kontrol et

## Önemli Notlar

1. **İlk deployment**: Uygulama ilk kez çalıştığında veritabanı oluşturulacak ve örnek veriler eklenecek
2. **Sonraki deploymentlar**: Veritabanı GCS'den indirilecek
3. **Veri kaybı**: Eğer GCS'de veritabanı yoksa, yeni bir tane oluşturulacak
4. **API key**: OpenAI API key'inin Secret Manager'da doğru ayarlandığından emin ol

## Gelecek İyileştirmeler

1. **Otomatik backup**: Düzenli veritabanı yedekleme
2. **Monitoring**: Daha detaylı loglama ve monitoring
3. **Error handling**: Daha kapsamlı hata yönetimi
4. **Performance**: Veritabanı performans optimizasyonu
