import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error,mean_squared_error
import joblib

df=pd.read_csv('slippage_sam.csv')


feature_col=['order_size','spread','depth_imbalance','volatility']
target_col='slippage'


missing_cols=[col for col in feature_col+[target_col] if col not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns in csv:{missing_cols}")

df=df.head(9)

X=df[feature_col]
Y=df[target_col]

X_train,X_test,y_train,y_test=train_test_split(X,Y,test_size=3,random_state=42)


lin_mod=LinearRegression()
lin_mod.fit(X_train,y_train)
y_pred_lin=lin_mod.predict(X_test)


print("linear reg results")
print("MAE:",mean_absolute_error(y_test,y_pred_lin))
print("MSE:",mean_squared_error(y_test,y_pred_lin))


joblib.dump(lin_mod,'lin_slip_model.pkl')


