#!/usr/bin/python3
# -*- utf-8 -*-
#
# Copyright (C) 2021-2023 Ken'ichi Fukamachi
#   All rights reserved. This program is free software; you can
#   redistribute it and/or modify it under 2-Clause BSD License.
#   https://opensource.org/licenses/BSD-2-Clause
#
# mailto: fukachan@fml.org
#    web: https://www.fml.org/
# github: https://github.com/fmlorg
#
# $FML: www.py,v 1.7 2023/04/07 06:57:31 fukachan Exp $
# $Revision: 1.7 $
#        NAME: www.py
# DESCRIPTION: a standalone web server based on python3 modules,
#              which is used as a template for our system build exercises.
#              See https://sysbuild-entrance.fml.org/ for more details.
#
import os
import sys
import http.server
import socketserver
import json
import random
import cgi
import boto3
#
# Configurations
#
HTTP_HOST       = "0.0.0.0"
HTTP_PORT       = 80
HTDOCS_DIR      = "/home/admin/htdocs"


# WWW server example: Handler class, which handles www requests
# httpHandler inherits ths superclass http.server.SimpleHTTPRequestHandler
class httpHandler(http.server.SimpleHTTPRequestHandler):
   def __init__(self, *args, **kwargs):
      super().__init__(*args, directory=HTDOCS_DIR, **kwargs)

   def _set_headers(self):
      self.send_response(200)
      self.send_header('Content-type','application/json; charset=utf-8')
      self.send_header('Access-Control-Allow-Origin', '*')
      self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
      self.send_header("Access-Control-Allow-Headers", "X-Requested-With, Access-Control-Allow-Origin")
      self.send_header("Access-Control-Allow-Credentials", "true")
      self.end_headers()

   def do_OPTIONS(self):
      self.send_response(200)
      self.send_header('Access-Control-Allow-Origin', '*')
      self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
      self.send_header("Access-Control-Allow-Headers", "X-Requested-With,Access-Control-Allow-Origin")
      self.send_header("Access-Control-Allow-Credentials", "true")
      self.end_headers()

   def do_GET(self):
      return super().do_GET()

   def do_POST(self):
      self._set_headers()
      data = {}
      if self.path =="/api/janken/v1":
          data = self.janken()
      if self.path =="/api/upload":
          data = self.play_janken_with_image()
      if self.path =="/api/text":
          data = self.textRekognize()

      message = json.dumps(data, ensure_ascii=False)
      self.wfile.write(bytes(message, "utf8"))

   def textRekognize(self):
       form = cgi.FieldStorage(
               fp=self.rfile,
               headers=self.headers,
               environ={'REQUEST_METHOD': 'POST'}
               )
       image_field = form['file']
       body = image_field.file.read()
       client = boto3.client('rekognition', 'us-east-1')
       response = client.detect_text(
               Image = { 'Bytes':body }
       )

       textData = response["TextDetections"][0]["DetectedText"]
       return textData


   def rekognize(self):
       form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
       )
       image_field = form['file']

       body = image_field.file.read()
       client = boto3.client('rekognition', 'us-east-1')
       response = client.detect_labels(
               Image = {
                   'Bytes':body
               }
       )

       hand = 3;
       selected_values = []
       selected_values.append(response["Labels"][0]["Name"])
       selected_values.append(response["Labels"][1]["Name"])
       selected_values.append(response["Labels"][2]["Name"])
       for i in range(len(selected_values)):
           if selected_values[i] == "Rock":
               hand = 0
           elif selected_values[i] == "Scissors":
               hand = 1
           elif selected_values[i] == "Paper":
               hand = 2

       return hand

   def play_janken_with_image(self):
       jibun = self.rekognize()
       if jibun == 3:
           return {"error":jibun}
       aite = random.randint(0,2)
       kekka = (3 + jibun- aite) % 3
       return {'jibun':jibun, 'aite':aite, 'kekka':kekka}


   def jibun(self):
       form = cgi.FieldStorage(
               fp=self.rfile,
               headers=self.headers,
               environ={'REQUEST_METHOD':'POST'}
       )
       key = form.getvalue('key')
       jibun = int(key)
       return jibun

   def aite(self):
       return random.randint(0,2)

   def janken(self):
       jibun = self.jibun()
       aite = self.aite()
       kekka = (3 + jibun - aite) % 3
       return {'jibun':jibun, 'aite':aite, 'kekka':kekka}

   def db_insert(self, jibun, aite, kekka):
      connection            = self.db_connect()
      connection.autocommit = True

      pass

      connection.close

   def db_show(self):
      connection            = self.db_connect()
      connection.autocommit = True

      pass

      connection.close


#
# MAIN
#
if __name__ == "__main__":
   # run python www server (httpd)
   with socketserver.TCPServer((HTTP_HOST, HTTP_PORT), httpHandler) as httpd:
      print("(debug) serving at port", HTTP_PORT, file=sys.stderr)
      httpd.serve_forever()