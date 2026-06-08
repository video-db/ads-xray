from videodb.editor import (
    Timeline,
    Track,
    Clip,
    VideoAsset,
    TextAsset,
    Fit,
    Position,
    Offset,
    Font,
    Background,
    TextAlignment,
    Border,
    Transition,
)


def _wrap_text(text: str, max_chars: int = 88) -> str:
    if len(text) <= max_chars:
        return text
    words = text.split()
    lines = []
    current = ""
    for w in words:
        if len(current) + len(w) + 1 <= max_chars:
            current = (current + " " + w) if current else w
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return "\n".join(lines)


def build_timeline(conn, video_id: str, total_duration: float, scenes: list[dict]) -> str:
    dur = int(float(total_duration))

    timeline = Timeline(conn)
    timeline.resolution = "1920x1080"
    timeline.background = "#000000"

    video_track = Track()
    video_track.add_clip(
        0,
        Clip(
            asset=VideoAsset(id=video_id, volume=1.0),
            duration=dur,
            fit=Fit.contain,
        ),
    )

    text_track = Track()
    for scene in scenes:
        start = int(scene["start"])
        overlay_dur = int(scene["duration"])
        if start + overlay_dur > dur:
            overlay_dur = dur - start
        if overlay_dur <= 0:
            continue

        wrapped = _wrap_text(scene["overlay_text"])
        lines = wrapped.count("\n") + 1
        box_height = 64 if lines == 1 else 64 + (lines - 1) * 40

        text_track.add_clip(
            start,
            Clip(
                asset=TextAsset(
                    text=wrapped,
                    width=1680,
                    font=Font(
                        family="Inter",
                        size=32,
                        color="#FFFFFF",
                    ),
                    background=Background(
                        width=1720,
                        height=box_height,
                        color="#0369A1",
                        opacity=0.95,
                        text_alignment=TextAlignment.center,
                    ),
                    border=Border(color="#0C4A6E", width=1.0),
                ),
                duration=overlay_dur,
                position=Position.center,
                offset=Offset(x=0, y=0.40),
                transition=Transition(in_="fade", out="fade", duration=0.3),
            ),
        )

    timeline.add_track(video_track)
    timeline.add_track(text_track)

    return timeline.generate_stream()
