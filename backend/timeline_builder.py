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
    Shadow,
    Transition,
)


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

        text_track.add_clip(
            start,
            Clip(
                asset=TextAsset(
                    text=scene["overlay_text"],
                    font=Font(
                        family="Inter",
                        size=28,
                        color="#FFFFFF",
                        opacity=1.0,
                    ),
                    background=Background(
                        width=1700,
                        height=80,
                        color="#0EA5E9",
                        opacity=0.85,
                        text_alignment=TextAlignment.center,
                    ),
                    border=Border(color="#38BDF8", width=1.5),
                    shadow=Shadow(color="#000000", x=0, y=2),
                ),
                duration=overlay_dur,
                position=Position.bottom,
                offset=Offset(x=0, y=-0.04),
                transition=Transition(in_="fade", out="fade", duration=0.3),
            ),
        )

    timeline.add_track(video_track)
    timeline.add_track(text_track)

    return timeline.generate_stream()
