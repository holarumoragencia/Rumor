#!/usr/bin/env bash
# Arma el audio del reel: voz (primera parte + voz en off recortada + final) y música de fondo baja,
# que se atenúa sola cuando hay voz y sube un poco en el cierre. Uso: mezcla.sh p1.mp4 voz.wav final.mp4 musica.mp3 salida.m4a
set -euo pipefail
P1=$1; VO=$2; FIN=$3; MUS=$4; OUT=$5
F='aformat=sample_rates=48000:channel_layouts=stereo'
ffmpeg -y -loglevel error -i "$P1" -i "$VO" -i "$FIN" -i "$MUS" -filter_complex "
[0:a]atrim=0:10.85,asetpts=PTS-STARTPTS,afade=t=out:st=10.80:d=0.05,$F[a0];
[1:a]atrim=0.90:21.75,asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st=20.80:d=0.05,$F[a1];
[2:a]atrim=0:5.45,asetpts=PTS-STARTPTS,afade=t=in:d=0.03,afade=t=out:st=5.40:d=0.05,$F[a2];
anullsrc=r=48000:cl=stereo,atrim=0:3.5[a3];
[a0][a1][a2][a3]concat=n=4:v=0:a=1[voz];
[voz]asplit[voz1][vozsc];
[3:a]atrim=0:40.65,asetpts=PTS-STARTPTS,$F,volume='if(lt(t,37.15),0.2,0.2+0.22*min(1,(t-37.15)/0.6))':eval=frame,afade=t=in:d=0.6,afade=t=out:st=39.2:d=1.45[mus];
[mus][vozsc]sidechaincompress=threshold=0.03:ratio=4:attack=20:release=450[musd];
[voz1][musd]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[out]" \
  -map "[out]" -c:a aac -b:a 192k "$OUT"
