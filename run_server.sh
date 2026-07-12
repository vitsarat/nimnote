#!/usr/bin/env bash
export NIMNOTE_HOME="$HOME/.nimnote_webtest"
cd /d/ROOM_NOOMNIM/nimnote
exec python -m nimnote.server
