"use client";

import { useState } from "react";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Card from "../components/ui/Card";

const API_BASE = "http://localhost:8000"; // change if different

export default function Page() {
  const [transcriptText, setTranscriptText] = useState("");
  const [audioFile, setAudioFile] = useState(null);
  const [txtFile, setTxtFile] = useState(null);
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingVideo, setLoadingVideo] = useState(false); // separate loading for video
  const [result, setResult] = useState(null);
  const [videoFile, setVideoFile] = useState(null); // Removed <File | null> type annotation
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [error, setError] = useState("");

  const uploadAudioFile = async () => {
    setError("");
    if (!audioFile) {
      setError("Select an audio file to upload.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const form = new FormData();
      form.append("file", audioFile);
      const res = await fetch(`${API_BASE}/analyze-audio/`, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Server error");
      // Show both transcript and analysis
      setResult(data);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalyzeText = async () => {
    setError("");
    if (!transcriptText.trim()) {
      setError("Provide transcript text or upload a .txt file.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      // send as JSON body with key `transcript` (match your backend)
      const res = await fetch(`${API_BASE}/analyze-text/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript: transcriptText }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Server error");
      setResult(data);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const uploadTxtFile = async () => {
    setError("");
    if (!txtFile) {
      setError("Select a .txt file to upload.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const form = new FormData();
      form.append("file", txtFile);
      const res = await fetch(`${API_BASE}/analyze-file/`, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Server error");
      setResult(data);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };

  const uploadPdfFile = async () => {
    setError("");
    if (!pdfFile) {
      setError("Select a .pdf file to upload.");
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const form = new FormData();
      form.append("file", pdfFile);
      const res = await fetch(`${API_BASE}/analyze-pitch-deck/`, { method: "POST", body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Server error");
      setResult(data);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  };


  const uploadVideo = async () => {
    setError("");
    if (!videoFile && !youtubeUrl.trim()) {
      setError("Provide a video file or YouTube link.");
      return;
    }
    setLoadingVideo(true); // separate loading for video
    setResult(null);
    try {
      const form = new FormData();
      if (videoFile) form.append("file", videoFile);
      if (youtubeUrl) form.append("youtube_url", youtubeUrl);

      const res = await fetch(`${API_BASE}/analyze-video/`, { // corrected route
        method: "POST",
        body: form,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Server error");
      setResult(data);

      // reset video inputs
      setVideoFile(null);
      setYoutubeUrl("");
    } catch (err) {
      setError(String(err));
    } finally {
      setLoadingVideo(false);
    }
  };

  return (
    <div className="space-y-8">
      <header className="flex flex-col sm:flex-row items-center justify-between gap-2 border-b pb-4 mb-4">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-800">Startup Pitch Analyzer</h1>
        <div className="text-sm text-slate-500">Frontend (Next.js) <span className="mx-1">&bull;</span> calls FastAPI</div>
      </header>

      {/* Analyze Transcript (text) */}
      <Card>
        <h2 className="text-lg font-semibold mb-2">Analyze Transcript (text or audio)</h2>
        <div className="flex flex-col md:flex-row gap-6">
          {/* Textarea for transcript */}
          <div className="flex-1">
            <textarea
              value={transcriptText}
              onChange={(e) => setTranscriptText(e.target.value)}
              rows={8}
              placeholder="Paste transcript here..."
              className="w-full p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 bg-white resize-none mb-3 shadow-sm"
            />
            <div className="flex gap-2">
              <Button onClick={fetchAnalyzeText} disabled={loading} className="w-36">
                {loading ? "Analyzing..." : "Analyze Text"}
              </Button>
              <Button onClick={() => { setTranscriptText(""); setResult(null); }} variant="secondary">
                Clear
              </Button>
            </div>
          </div>
          {/* Audio upload */}
          <div className="flex-1 flex flex-col gap-2">
            <label className="font-medium mb-1">Or upload audio file</label>
            <input
              type="file"
              accept="audio/*,.wav,.mp3,.m4a,.ogg"
              onChange={e => setAudioFile(e.target.files?.[0] ?? null)}
              className="block w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            <Button onClick={uploadAudioFile} disabled={loading} className="w-44">
              {loading ? "Processing..." : "Upload & Analyze Audio"}
            </Button>
            {audioFile && <div className="text-xs text-slate-600">{audioFile.name}</div>}
          </div>
        </div>
      </Card>

      {/* Upload Transcript (.txt) */}
      <Card>
        <h2 className="text-lg font-semibold mb-2">Upload Transcript (.txt)</h2>
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <input
            type="file"
            accept=".txt"
            onChange={(e) => setTxtFile(e.target.files?.[0] ?? null)}
            className="block w-full sm:w-auto text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <Button onClick={uploadTxtFile} disabled={loading}>
            {loading ? "Uploading..." : "Upload & Analyze .txt"}
          </Button>
          {txtFile && <div className="text-sm text-slate-600">{txtFile.name}</div>}
        </div>
      </Card>

      {/* Upload Pitch Deck (.pdf) */}
      <Card>
        <h2 className="text-lg font-semibold mb-2">Upload Pitch Deck (.pdf)</h2>
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setPdfFile(e.target.files?.[0] ?? null)}
            className="block w-full sm:w-auto text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
          />
          <Button onClick={uploadPdfFile} disabled={loading}>
            {loading ? "Processing..." : "Upload & Analyze .pdf"}
          </Button>
          {pdfFile && <div className="text-sm text-slate-600">{pdfFile.name}</div>}
        </div>
        <div className="text-xs text-slate-400 mt-1">Note: PDF processing may take some time depending on your backend AI calls.</div>
      </Card>


       {/* Video Section */}
      <Card>
        <h2 className="text-lg font-semibold mb-2">Transcribe Video (File or YouTube Link)</h2>
        <div className="flex flex-col gap-4">
          <div>
            <label className="font-medium mb-1">Upload Video File</label>
            <input
              type="file"
              accept="video/*,.mp4,.mov,.avi,.mkv"
              onChange={(e) => setVideoFile(e.target.files?.[0] ?? null)}
              className="block w-full text-sm text-slate-600 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            {videoFile && <div className="text-xs text-slate-600 mt-1">{videoFile.name}</div>}
          </div>

          <div>
            <label className="font-medium mb-1">Or paste YouTube link</label>
            <input
              type="text"
              value={youtubeUrl}
              onChange={(e) => setYoutubeUrl(e.target.value)}
              placeholder="https://youtube.com/watch?v=..."
              className="w-full p-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>

          <Button onClick={uploadVideo} disabled={loadingVideo} className="w-52">
            {loadingVideo ? "Processing..." : "Transcribe Video"}
          </Button>
        </div>
      </Card>

      {/* Result Section */}
      <Card>
        <h2 className="text-lg font-semibold mb-2">Result</h2>
        {error && <div className="text-red-500 font-medium mb-2">{error}</div>}
        {result ? (
          result.transcript && result.analysis ? (
            <>
              <div className="mb-2">
                <span className="font-semibold">Transcript:</span>
                <pre className="bg-slate-50 p-2 rounded text-xs overflow-x-auto border border-slate-200 max-h-40 mt-1">{result.transcript}</pre>
              </div>
              <div>
                <span className="font-semibold">Analysis:</span>
                <pre className="bg-slate-100 p-3 rounded text-sm overflow-x-auto mt-2 border border-slate-200 max-h-96">{JSON.stringify(result.analysis, null, 2)}</pre>
              </div>
            </>
          ) : (
            <pre className="bg-slate-100 p-3 rounded text-sm overflow-x-auto mt-2 border border-slate-200 max-h-96">{JSON.stringify(result, null, 2)}</pre>
          )
        ) : !loading && <div className="text-slate-400">No result yet.<br/>Backend: {API_BASE}</div>}
      </Card>

      <footer className="text-sm text-slate-500">Backend: {API_BASE}</footer>
    </div>
  );
}
