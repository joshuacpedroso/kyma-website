<?php
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
readfile(__DIR__.'/index.html');
