# Copyright 2019-2019 Gryphon Zone
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
FROM python:3-alpine

COPY requirements.txt /tmp/requirements.txt
COPY printconfig.sh /tmp/printconfig.sh

RUN apk add --no-cache build-base \
  && pip install --upgrade pip \
  && pip install --upgrade -r /tmp/requirements.txt \
  && sh /tmp/printconfig.sh \
  && pip uninstall --yes pip \
  && apk del build-base

EXPOSE 8080

COPY python/ /tmp/python

ENTRYPOINT ["python", "/tmp/python/main.py"]
