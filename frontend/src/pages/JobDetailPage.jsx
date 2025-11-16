import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Loader, CheckCircle, XCircle, Film } from 'lucide-react';
import { getJob } from '../services/api';

function JobDetailPage() {
  const { jobId } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchJob();

    // Poll for updates while processing
    const interval = setInterval(() => {
      if (job && (job.status === 'pending' || job.status === 'processing')) {
        fetchJob();
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobId, job?.status]);

  const fetchJob = async () => {
    try {
      const data = await getJob(jobId);
      setJob(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch job:', err);
      setError('Failed to load job details');
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '-';
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <Loader className="h-8 w-8 text-primary-600 animate-spin" />
      </div>
    );
  }

  if (error || !job) {
    return (
      <div className="card bg-red-50 border border-red-200">
        <p className="text-red-800">{error || 'Job not found'}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Back Button */}
      <button
        onClick={() => navigate('/jobs')}
        className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
      >
        <ArrowLeft className="h-5 w-5" />
        <span>Back to Jobs</span>
      </button>

      {/* Job Info */}
      <div className="card">
        <div className="flex items-start justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {job.filename}
            </h1>
            <div className="space-y-1 text-sm text-gray-600">
              <p>Created: {formatDate(job.created_at)}</p>
              <p>Size: {formatFileSize(job.file_size)}</p>
              {job.duration && <p>Duration: {formatDuration(job.duration)}</p>}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {job.status === 'pending' && (
              <>
                <Loader className="h-5 w-5 text-gray-400" />
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                  Pending
                </span>
              </>
            )}
            {job.status === 'processing' && (
              <>
                <Loader className="h-5 w-5 text-primary-600 animate-spin" />
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-primary-100 text-primary-800">
                  Processing
                </span>
              </>
            )}
            {job.status === 'completed' && (
              <>
                <CheckCircle className="h-5 w-5 text-green-600" />
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                  Completed
                </span>
              </>
            )}
            {job.status === 'failed' && (
              <>
                <XCircle className="h-5 w-5 text-red-600" />
                <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                  Failed
                </span>
              </>
            )}
          </div>
        </div>

        {/* Progress Bar */}
        {job.progress && job.status === 'processing' && (
          <div className="mb-6">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="font-medium text-gray-700">
                {job.progress.message}
              </span>
              <span className="text-gray-600">
                {Math.round(job.progress.progress)}%
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-primary-600 h-3 rounded-full transition-all duration-300"
                style={{ width: `${job.progress.progress}%` }}
              />
            </div>
            {job.progress.current_clip && job.progress.total_clips && (
              <p className="text-xs text-gray-500 mt-1">
                Clip {job.progress.current_clip} of {job.progress.total_clips}
              </p>
            )}
          </div>
        )}

        {/* Error Message */}
        {job.error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg mb-6">
            <p className="text-sm text-red-800">{job.error}</p>
          </div>
        )}

        {/* Clips Section */}
        {job.status === 'completed' && job.clips_count > 0 && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Generated Clips ({job.clips_count})
              </h2>
              <Link
                to={`/jobs/${jobId}/clips`}
                className="btn btn-primary flex items-center space-x-2"
              >
                <Film className="h-5 w-5" />
                <span>View Clips</span>
              </Link>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm text-green-800">
                Processing complete! {job.clips_count} clips have been generated
                and are ready to download.
              </p>
            </div>
          </div>
        )}

        {/* Processing Info */}
        {job.status === 'processing' && (
          <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
            <p className="text-sm text-primary-800">
              Your video is being processed. This may take a few minutes depending
              on the video length and server load.
            </p>
          </div>
        )}
      </div>

      {/* Video Preview (if available) */}
      {job.video_url && (
        <div className="card">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Original Video
          </h2>
          <video
            controls
            className="w-full max-w-3xl mx-auto rounded-lg"
            src={job.video_url}
          >
            Your browser does not support the video tag.
          </video>
        </div>
      )}
    </div>
  );
}

export default JobDetailPage;
