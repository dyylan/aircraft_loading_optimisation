FROM python:3.6-alpine

RUN adduser -D main

WORKDIR /home/main

COPY requirements.txt requirements.txt

RUN python -m venv venv
RUN apk add --no-cache --virtual .build-deps gcc musl-dev file make dos2unix 
#g++ subversion openblas

# Make and install COIN-OR
#RUN svn checkout https://projects.coin-or.org/svn/CoinBinary/OptimizationSuite/stable/1.8 COIN-1.8 && \
#    cd COIN-1.8 && \
#    ./configure && \
#    make && \
#    make install && \
#    cd ..

# Make and install GLPK
RUN wget ftp://ftp.gnu.org/gnu/glpk/glpk-4.65.tar.gz && \
    tar -xzvf glpk-4.65.tar.gz && \
    cd glpk-4.65 && \
    ./configure && \
    make install && \
    cd ..

RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn gevent

RUN apk del .build-deps gcc musl-dev 

COPY static static
COPY templates templates
COPY main.py forms.py blocks.py lp.py startup.sh ./

RUN chmod +x startup.sh
RUN dos2unix startup.sh

ENV FLASK_APP main.py

RUN chown -R main:main ./
USER main 

EXPOSE 5000
ENTRYPOINT ["./startup.sh"]