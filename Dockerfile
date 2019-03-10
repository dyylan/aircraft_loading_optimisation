FROM python:3.6-alpine

ENV GLPK_VER 4.65

RUN adduser -D main

WORKDIR /home/main

COPY requirements.txt requirements.txt

RUN python -m venv venv
RUN apk add --no-cache --virtual .build-deps gcc musl-dev file make

# Make and install GLPK
#RUN wget http://ftp.gnu.org/gnu/glpk/glpk-$GLPK_VER.tar.gz && \
#    tar -xvzf glpk-$GLPK_VER.tar.gz && cd glpk-$GLPK_VER && \
#    ./configure --prefix=/usr && make && make check && \
#    make install && make distclean && \
#    cd .. && rm -Rf glpk-$GLPK_VER && rm glpk-$GLPK_VER.tar.gz

RUN wget ftp://ftp.gnu.org/gnu/glpk/glpk-4.65.tar.gz && \
    tar -xzvf glpk-4.65.tar.gz && \
    cd glpk-4.65 && \
    ./configure && \
    make install

RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn
RUN apk del .build-deps gcc musl-dev

COPY static static
COPY templates templates
COPY main.py forms.py blocks.py lp.py startup.sh ./

RUN chmod +x startup.sh

ENV FLASK_APP main.py

RUN chown -R main:main ./
USER main

EXPOSE 5000
ENTRYPOINT ["./startup.sh"]