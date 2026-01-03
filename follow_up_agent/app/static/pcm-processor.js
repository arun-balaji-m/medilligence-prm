class PCMProcessor extends AudioWorkletProcessor {
    process(inputs) {
        const input = inputs[0];
        if (input && input[0]) {
            const channelData = input[0];
            const pcm16 = new Int16Array(channelData.length);

            for (let i = 0; i < channelData.length; i++) {
                pcm16[i] = Math.max(-1, Math.min(1, channelData[i])) * 32767;
            }

            this.port.postMessage(pcm16.buffer, [pcm16.buffer]);
        }
        return true;
    }
}

registerProcessor("pcm-processor", PCMProcessor);
