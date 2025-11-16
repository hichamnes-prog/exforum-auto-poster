import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Film, Clock, CheckCircle, XCircle, Loader } from 'lucide-react';
import { getJobs } from '../services/api';

function JobsPage() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchJobs();

    // Poll for updates every 3 seconds
    const interval = setInterval(fetchJobs, 3000);

    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    try {
      const data = await getJobs();
      setJobs(data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to fetch jobs:', err);
      setError('Failed to load jobs');
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="h-5 w-5 text-gray-400" />;
      case 'processing':
        return <Loader className="h-5 w-5 text-primary-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case 'failed':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusText = (status) => {
    return status.charAt(0).toUpperCase() + status.slice(1);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-gray-100 text-gray-800';
      case 'processing':
        return 'bg-primary-100 text-primary-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
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

  if (jobs.length === 0) {
    return (
      <div className="text-center py-12">
        <Film className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <h2 className="text-xl font-semibold text-gray-900 mb-2">No jobs yet</h2>
        <p className="text-gray-600 mb-6">Upload a video to get started!</p>
        <Link to="/" className="btn btn-primary">
          Upload Video
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Your Jobs</h1>
        <Link to="/" className="btn btn-primary">
          Upload New Video
        </Link>
      </div>

      <div className="space-y-4">
        {jobs.map((job) => (
          <Link
            key={job.id}
            to={`/jobs/${job.id}`}
            className="card hover:shadow-lg transition-shadow block"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4 flex-1">
                <div className="flex-shrink-0">
                  <Film className="h-10 w-10 text-primary-600" />
                </div>

                <div className="flex-1 min-w-0">
                  <h3 className="text-lg font-semibold text-gray-900 truncate">
                    {job.filename}
                  </h3>
                  <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                    <span>{formatDate(job.created_at)}</span>
                    {job.duration && (
                      <span>Duration: {formatDuration(job.duration)}</span>
                    )}
                    {job.clips_count > 0 && (
                      <span>{job.clips_count} clips</span>
                    )}
                  </div>

                  {/* Progress */}
                  {job.progress && (
                    <div className="mt-2">
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span className="text-gray-600">{job.progress.message}</span>
                        <span className="text-gray-600">{Math.round(job.progress.progress)}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${job.progress.progress}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Error */}
                  {job.error && (
                    <p className="mt-2 text-sm text-red-600">{job.error}</p>
                  )}
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(
                    job.status
                  )}`}
                >
                  {getStatusText(job.status)}
                </span>
                {getStatusIcon(job.status)}
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default JobsPage;
