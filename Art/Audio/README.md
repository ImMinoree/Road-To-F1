# Kart audio and commentary

Engine audio is an original procedural two-stroke approximation, generated per kart. Speed and throttle change firing frequency. Player audio is foreground; opponents attenuate and pan in world space. Burning engines go silent. Commentary temporarily lowers engine volume.

The five WAVs in Art/Audio/Commentary are temporary Windows SAPI synthetic speech, not the user's voice. Corresponding original scripts are in lines.json. Unreal assets live at /Game/RoadToF1/Audio/CommentaryV01 and are assigned through the race director's Commentary Clips map. Captions remain available when clips are absent. Start, lap, overtake, incident and finish events drive commentary; an eight-second cooldown limits routine callouts, while lap and finish milestones take priority. F5 resets commentary state.

To replace the voice: record each line as a separate dry WAV, preferably mono 48kHz, without music or engine noise, leaving a short pause around speech. Deliver the files using the five cue names. Reimport into the same Unreal assets to preserve assignments. No voice cloning or microphone recording happens in the game.

HUD speeds are mph. Movement limits remain 57/55 km/h (35.4/34.2 mph), and training telemetry retains its documented km/h schema. The left tower shows player lap and forward centreline distance to the lap line in feet, plus each racer's lap alongside identity and speed. Distance is an estimate along the authored track, not validation that checkpoints were passed. Round badges above the helmets identify all 20 racers with suit-coloured shells, white centres and black numbers; they face the camera within 45 metres.
