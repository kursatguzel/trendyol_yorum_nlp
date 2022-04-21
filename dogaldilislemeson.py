# -*- coding: utf-8 -*-
"""dogaldilislemeson.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fktTmzujvHvHIn9nfen_4pu5IDxGu32g

# Bağlantı
"""

!apt-get install -y -qq software-properties-common python-software-properties module-init-tools
!add-apt-repository -y ppa:alessandro-strada/ppa 2>&1 > /dev/null
!apt-get update -qq 2>&1 > /dev/null
!apt-get -y install -qq google-drive-ocamlfuse fuse
from google.colab import auth
auth.authenticate_user()
from oauth2client.client import GoogleCredentials
creds = GoogleCredentials.get_application_default()
import getpass
!google-drive-ocamlfuse -headless -id={creds.client_id} -secret={creds.client_secret} < /dev/null 2>&1 | grep URL
vcode = getpass.getpass()
!echo {vcode} | google-drive-ocamlfuse -headless -id={creds.client_id} -secret={creds.client_secret}

!mkdir -p drive
!google-drive-ocamlfuse drive
!ls

"""# Veri Seti Yükleme"""

import pandas as pd
import numpy as np
# csv den veri yükleme

from openpyxl import Workbook,load_workbook 
yorumlar = pd.read_excel('/content/drive/Colab Notebooks/trendyolveri/trendyolverislenmis.xlsx')
#data = pd.read_csv('/content/drive/Colab Notebooks/hepsiburadaveri/reviews2.txt', delimiter='\t')

#data = data.sample(frac=1).reset_index(drop=True)

#filitreleme büyük harf/ küçük harf
import re
import nltk
# gereksiz kelimler çıkarma
from nltk.stem.porter import PorterStemmer
# ps ingilizce için türkçede deniyeceğim
ps = PorterStemmer()
nltk.download('stopwords')
from nltk.corpus import stopwords
yorumdizim=[]
for i in range(98): # execelde kolon uzunluğu 98 di
    # Yorumlar bizim verilerde ki başlık
    data = re.sub('[^a-zA-Z]',' ',yorumlar['Yorumlar'][i])
    # Küçük harfe çevirme
    data = data.lower()
    # listeye çevirme
    data=data.split()
    # Önemli set ile küme yapıyoruz bunun nedeni aynı ifade birden fazla geçmemesi için
    # eğer kelime listede yoksa stemle yani listenin ilk elemanı yap
    data = [ps.stem(kelime) for kelime in data if not kelime in set(stopwords.words('turkish'))]
    # şunu dene olmazsa
    # data = [yorum.stem(kelime) for kelime in data ]
    # data değişkenini boşluklarla birleştir
    data = ' '.join(data)
    yorumdizim.append(data)
from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer(max_features=2000)
#bağımsız değişken
X = cv.fit_transform(yorumdizim).toarray()
# bağımlı değişken
y = yorumlar.iloc[:,1].values # [:,1] bütün satırlar ve 1. kolon
#from sklearn.cross_decomposition import train_test_split
from sklearn.model_selection import train_test_split
# Test ve eğitim için bölme
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)
from sklearn.naive_bayes import MultinomialNB
gnb= MultinomialNB()
#X_test_counts = count_vect.transform(X_test)
#X_test_tfidf = tfidf_transformer.transform(X_test_counts)

##from sklearn.naive_bayes import GaussianNB
##gnb = GaussianNB()
# X_train den y_train i öğren diyeceğiz
gnb.fit(X_train,y_train) # fit öğretmek için kullanılır
# X_test tahmin et diyeceğiz ve y_test ile karşılaştıracağız
y_pred = gnb.predict(X_test) #predict tahmin için kullandık
# şimdide gerçek verilerle karşılaştır diyeceğiz
from sklearn.metrics import confusion_matrix
# başarı oranına bakacağız
cm = confusion_matrix(y_test, y_pred)
print(cm)

data.head() #ilk beş girdi görmek için

"""Metinlerin pozitif, negatif ve nötr durumları"""

data['beklentimin altında bir ürün kaliteli değil'].value_counts()

"""# Veri Seti Önişleme"""

import string #noktalama işaretleri
import re
import nltk #etkisiz kelimeler
from nltk.corpus import stopwords
nltk.download('stopwords') # önemliiiii
noktalama = string.punctuation
etkisiz = stopwords.words('turkish')
print(noktalama)
print(etkisiz)

for d in data['beklentimin altında bir ürün kaliteli değil'].head():
  print(d+ '\n------------------------------')
  # Etkisiz kelimeleri atmak
  temp= ''
  for word in d.split():
    if word not in etkisiz and not word.isnumeric():
        temp += word + ''
  print(temp+ '\n********************')

"""Noktalama işaretleri silme"""

for d in data['beklentimin altında bir ürün kaliteli değil'].head():
  print(d+ '\n------------------------------')
  # Noktalama işaretleri atma
  temp= ''
  for word in d:
    if word not in noktalama:
        temp += word
  print(temp+ '\n********************')
  d= temp

"""Verileri kayıt etme"""

data.to_csv(r'/content/drive/Colab Notebooks/Hepsiburadaveri/cleaned.csv',index=False)



"""# Arındılımış veri yükleme"""

import pandas as pd
data = pd.read_csv('/content/drive/Colab Notebooks/Hepsiburadaveri/cleaned.csv', sep=",", names=['review', 'label'])
print(data.head())

from sklearn.feature_extraction.text import CountVectorizer
cv = CountVectorizer(max_features = 100)

"""# Veri Setini Bölme"""

# Arındırılmış veriyi train ve test kümelerine ayırıyoruz
from sklearn.model_selection import train_test_split
# Eğitim ve test olarak ayıracağız. train=eğitim, test=test
X_train, X_test, y_train, y_test = train_test_split(data['review'].values.astype('U'),data['label'].values.astype('U'), test_size=0.1, random_state=42)
print(X_train.shape)
#print(Xtest.shape)

"""# Sayma Vektörü Oluşturma"""

# Train kümesindeki cümlelerin sayma vektöelerini çıkarıyoruz
from sklearn.feature_extraction.text import CountVectorizer
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(X_train)
print(X_train_counts.shape)

"""Tf*Idf vektörü oluşturma
sadece o yoruma özgü(temsil edecek kelimler olmalı)
"""

# Train kümesindeki cümlelerin TF*IDF vektörlerini sayma vekttörlerinden oluşturuyoruz
# Tf= terim sıklığı, IDF= bir kelimenin dökümanda kaç kere geçtiği
# TF*IDF bütün olarak; bir kelimenin bir döküman içinde ki önemini gösterir
from sklearn.feature_extraction.text import TfidfTransformer
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
print(X_train_tfidf.shape)

"""# Naive Bayes Model Eğitimi"""

# Çok modlu Naive Bayes Sınıflandırıcısı eğitiyoruz
from sklearn.naive_bayes import MultinomialNB
clf = MultinomialNB().fit(X_train_tfidf, y_train)
X_test_counts = count_vect.transform(X_test)
X_test_tfidf = tfidf_transformer.transform(X_test_counts)

"""# Model Performansı Ölçme"""

# Sınıflandırıcı ile test seti üzerindeki tahminleme yapıyoruz
y_pred = clf.predict(X_test_tfidf)
for review, sentiment in zip(X_test[:5], y_pred[:]):
  print('%r => %s' % (review, sentiment))

"""Test Sonuçları"""

# Performans sonuçları
from sklearn.metrics import accuracy_score
print(accuracy_score(y_test, y_pred))

