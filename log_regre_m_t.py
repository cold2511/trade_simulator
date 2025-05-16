import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report
import joblib

df=pd.read_csv('okx_trades.csv')

df['timestamp']=pd.to_datetime(df['timestamp'],unit='ms')
df['seconds']=df['timestamp'].astype('int64')//10**9
df['price']=pd.to_numeric(df['price'],errors='coerce')
df['size']=pd.to_numeric(df['size'],errors='coerce')

df.dropna(inplace=True)

df['label']=df['side'].apply(lambda x:1 if x=='buy' else 0)

X=df[['price','size','seconds']]
Y=df['label']

X_train,X_test,y_train,y_test=train_test_split(X,Y,stratify=Y,test_size=0.2,random_state=42)


scaler=StandardScaler()
X_train=scaler.fit_transform(X_train)
X_test=scaler.transform(X_test)

model=LogisticRegression()
model.fit(X_train,y_train)

y_pred=model.predict(X_test)
print("evaluation")
print(classification_report(y_test,y_pred,target_names=["Taker Sell","Taker Buy"]))
joblib.dump(model,'mak_tak_log_model.pkl')
joblib.dump(scaler,'scaler.pkl')
