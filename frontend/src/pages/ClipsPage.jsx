import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Scissors, Play, Loader } from 'lucide-react';
import { getClips, trimClip } from '../services/api';

function ClipsPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [clips, setClips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedClip, setSelectedClip] = useState(null);
  const [trimming, setTrimming] = useState(false);
  const [trimStart, setTrimStart] = useState(0);
  const [trimEnd, setTrimEnd] = useState(0);

  useEffect(() => {
    fetchClips();
  }, [jobId]);

  const fetchClips = async () => {
    try {
      const data = await getClips(jobId);
      setClips(data.clips);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch clips:', err);
      setError('Failed to load clips');
      setLoading(false);
    }
  };

  const handleTrimClip = async () => {
    if (!selectedClip || trimStart >= trimEnd) return;

    setTrimming(true);

    try {
      const updatedClip = await trimClip(
        jobId,
        selectedClip.id,
        trimStart,
        trimEnd,
        selectedClip.aspect_ratio
      );

      // Update clips list
      setClips(
        clips.map((c) => (c.id === selectedClip.id ? updatedClip : c))
      );

      setSelectedClip(null);
      setTrimming(false);
    } catch (err) {
      console.error('Failed to trim clip:', err);
      alert('Failed to trim clip. Please try again.');
      setTrimming(false);
    }
  };

  const openTrimDialog = (clip) => {
    setSelectedClip(clip);
    setTrimStart(clip.start_time);
    setTrimEnd(clip.end_time);
  };

  const formatTime = (seconds) => {
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    const ms = Math.floor((seconds % 1) * 10);
    return `${minutes}:${secs.toString().padStart(2, '0')}.${ms}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader className="h-8 w-8 text-primary-600 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <p className="text-red-800">{error}</p>
      </div>
    );
  }

  if (clips.length === 0) {
    return (
      <div className="text-center py-12">
        <Play className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">
          No clips generated yet
        </h2>
        <p className="text-gray-600">
          The processing may still be in progress.
        </p>
      </div>
    );
  }

  // Group clips by aspect ratio
  const clipsByRatio = clips.reduce((acc, clip) => {
    if (!acc[clip.aspect_ratio]) {
      acc[clip.aspect_ratio] = [];
    }
    acc[clip.aspect_ratio].push(clip);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => navigate(`/jobs/${jobId}`)}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="h-5 w-5" />
          <span>Back to Job</span>
        </button>

        <h1 className="text-3xl font-bold text-gray-900">
          Generated Clips ({clips.length})
        </h1>
      </div>

      {/* Clips by Aspect Ratio */}
      {Object.entries(clipsByRatio).map(([ratio, ratioClips]) => (
        <div key={ratio} className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900">
            {ratio === '9:16' && 'Vertical (Stories/Reels)'}
            {ratio === '16:9' && 'Landscape (YouTube)'}
            {ratio === '1:1' && 'Square (Feed)'}
            {!['9:16', '16:9', '1:1'].includes(ratio) && ratio}
            <span className="ml-2 text-sm font-normal text-gray-600">
              ({ratioClips.length} clips)
            </span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {ratioClips.map((clip, index) => (
              <div key={clip.id} className="card">
                {/* Video Player */}
                <div className="relative bg-gray-900 rounded-lg overflow-hidden mb-4">
                  <video
                    controls
                    className="w-full"
                    src={clip.video_url}
                    poster={clip.thumbnail_url}
                  >
                    Your browser does not support the video tag.
                  </video>
                </div>

                {/* Clip Info */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-900">
                      Clip {index + 1}
                    </span>
                    <span className="text-xs text-gray-500">
                      Score: {(clip.score * 100).toFixed(0)}%
                    </span>
                  </div>

                  <div className="text-xs text-gray-600 space-y-1">
                    <p>
                      Time: {formatTime(clip.start_time)} -{' '}
                      {formatTime(clip.end_time)}
                    </p>
                    <p>Duration: {formatTime(clip.duration)}</p>
                  </div>

                  {/* Transcript Preview */}
                  {clip.transcript && (
                    <p className="text-xs text-gray-600 line-clamp-2">
                      {clip.transcript}
                    </p>
                  )}

                  {/* Actions */}
                  <div className="flex space-x-2">
                    <a
                      href={clip.video_url}
                      download
                      className="flex-1 btn btn-primary text-sm flex items-center justify-center space-x-1"
                    >
                      <Download className="h-4 w-4" />
                      <span>Download</span>
                    </a>

                    <button
                      onClick={() => openTrimDialog(clip)}
                      className="flex-1 btn btn-secondary text-sm flex items-center justify-center space-x-1"
                    >
                      <Scissors className="h-4 w-4" />
                      <span>Trim</span>
                    </button>
                  </div>

                  {/* Download Captions */}
                  {clip.caption_url && (
                    <a
                      href={clip.caption_url}
                      download
                      className="text-xs text-primary-600 hover:underline block text-center"
                    >
                      Download SRT Captions
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Trim Dialog */}
      {selectedClip && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-2xl w-full p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">
              Trim Clip
            </h3>

            {/* Video Preview */}
            <video
              controls
              className="w-full mb-4 rounded-lg"
              src={selectedClip.video_url}
            >
              Your browser does not support the video tag.
            </video>

            {/* Trim Controls */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Time (seconds)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min={0}
                  max={selectedClip.end_time}
                  value={trimStart}
                  onChange={(e) => setTrimStart(parseFloat(e.target.value))}
                  className="input"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Time (seconds)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min={trimStart}
                  max={selectedClip.duration * 2}
                  value={trimEnd}
                  onChange={(e) => setTrimEnd(parseFloat(e.target.value))}
                  className="input"
                />
              </div>

              <p className="text-sm text-gray-600">
                New duration: {formatTime(trimEnd - trimStart)}
              </p>
            </div>

            {/* Actions */}
            <div className="flex space-x-4 mt-6">
              <button
                onClick={handleTrimClip}
                disabled={trimming || trimStart >= trimEnd}
                className="flex-1 btn btn-primary"
              >
                {trimming ? 'Trimming...' : 'Apply Trim'}
              </button>

              <button
                onClick={() => setSelectedClip(null)}
                disabled={trimming}
                className="flex-1 btn btn-secondary"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ClipsPage;
