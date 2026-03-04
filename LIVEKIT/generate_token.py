from livekit.api import AccessToken, VideoGrants

token = (
    AccessToken("devkey", "secret")
    .with_identity("test-user")
    .with_name("Test User")
    .with_grants(VideoGrants(room_join=True, room="test-room"))
    .to_jwt()
)

print(token)