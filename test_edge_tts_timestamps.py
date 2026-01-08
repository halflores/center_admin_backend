
import asyncio
import edge_tts

async def test_timestamps():
    text = "Hello world. This is a test."
    voice = "en-US-AriaNeural"
    communicate = edge_tts.Communicate(text, voice)
    
    print(f"Generating audio for: '{text}'")
    
    async for chunk in communicate.stream():
        if chunk["type"] == "WordBoundary":
            print(f"Word: {chunk}")
        elif chunk["type"] == "audio":
            # Just ignore audio data for this test
            pass

if __name__ == "__main__":
    asyncio.run(test_timestamps())
