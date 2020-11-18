FROM python:3.6

WORKDIR /app

ENV LC_ALL='C.UTF-8'
ENV LANG='C.UTF-8'

RUN pip3 install pipenv
RUN pip3 install pyinstaller

RUN curl -sL https://deb.nodesource.com/setup_10.x | bash -
RUN apt-get install -y nodejs git
RUN npm install --global release-it

RUN git config --global user.email "iljamoisejevs@gmail.com"
RUN git config --global user.name "ilmoi"

COPY . /app/

RUN mkdir -p /root/.ssh
COPY id_rsa /root/.ssh
COPY known_hosts /root/.ssh

CMD ./release.sh