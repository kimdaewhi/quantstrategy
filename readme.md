## 가상환경 구성
### 1. 해당 폴더에서 다음 명령어 실행  
```python -m venv .venv```  
```.\.venv\Scripts\Activate```  
```.venv\bin\activate```

### 2. 필요한 패키지 설치
```pip install [패키지명]```  

-- 패키지 목록 관리  
```pip freeze > [requirements.txt]```  

-- 필요할 때 패키지 파일 이용한 패키지 설치  
```pip install -r [requirements.txt]```

```Ctrl``` + ```Shift``` + ```P``` > Python: Select Interpreter > 가성환경 인터프리터 선택

-- 가상환경 비활성화
```deactivate```


### 3. 가상환경 이용하여 패키지 설치
가상환경 실행 명령어  
```.\.venv\Scripts\Activate```

### 4. 패키지 설치
```pip install backtrader```  
```pip install zipline-reloaded```
> zipline-reloaded 패키지 설치시 오류 해결법(👉🏻웬만하면 파이썬 3.5ver 이하로 쓰자..😑😑)  
https://velog.io/@havanafrog/ta-lib-errorta-lib-%EC%84%A4%EC%B9%98-%EC%98%A4%EB%A5%98
https://github.com/cgohlke/talib-build/releases  
파이썬 버전 확인 ex) 3.12.2 = cpp_312어쩌고

```pip install pyalgotrade```
```pip install yfinance```
```pip install finance-datareader```

-----

### backtrader 정리

1. 전략 class는 backtrader의 Strategy를 상속받아서 사용한다.
    ```python
    import backtrader as bt
    .
    .
    .
    class MyStrategy(bt.Strategy):
        def log:
            .
            .
    ```

2. ```bt.Strategy``` 클래스에서 제공하는 기본 메서드 종류
   - ```__init__``` : 인스턴스 초기화 시 사용하는 메서드
   - ```notify__order``` : 주문 상태 변경을 알리기 위한 메서드. 주문 제출, 접수, 완료, 취소 등
   - ```next``` : 매일 호출되는 메서드. 새로운 데이터가 입력될 때마다 호출되어 트레이딩 로직을 실행함.
   - ```stop``` : 백테스트가 종료될 때 호출되는 메서드