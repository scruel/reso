'use client'

import { FC, useEffect, useState } from "react";
import axios from "axios";
import ErrorPage from "@/components/ErrorPage";
import { BarChart3, Users, TrendingUp, AlertCircle } from "lucide-react";

interface LogData {
  totalEvents: number;
  uniqueUsers: number;
  topCategories: string[];
  topSearches: { query: string; count: number }[];
  topClicks: { product: string; count: number }[];
  hourlyTimeline: { hour: string; count: number }[];
  recentActivity: { timestamp: string; action: string }[];
}

const AnalyticsPage: FC = () => {
  const [logData, setLogData] = useState<LogData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<any>(null);

  useEffect(() => {
    const fetchLogData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const response = await axios.get("/api/analytics");
        setLogData(response.data);
      } catch (err) {
        console.error("Error fetching analytics data", err);
        setError(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLogData();
  }, []);

  if (isLoading) {
    return (
      <>
        <div className="fixed top-0 left-0 right-0 z-50 bg-gray-100 backdrop-blur-sm h-12 flex items-center px-6">
          <div className="text-xl font-medium tracking-wide text-sky-600">Reso</div>
        </div>
        
        <div className="min-h-screen bg-gray-100 pt-12 flex items-center justify-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="animate-spin rounded-full h-12 w-12 border-4 border-sky-600 border-t-transparent"></div>
            <div className="animate-pulse text-gray-500 text-lg">載入分析數據中...</div>
          </div>
        </div>
      </>
    );
  }

  if (error) {
    return <ErrorPage error={error} />;
  }

  if (!logData) {
    return (
      <>
        <div className="fixed top-0 left-0 right-0 z-50 bg-gray-100 backdrop-blur-sm h-12 flex items-center px-6">
          <div className="text-xl font-medium tracking-wide text-sky-600">Reso</div>
        </div>
        
        <div className="min-h-screen bg-gray-100 pt-12 flex items-center justify-center">
          <div className="max-w-2xl mx-auto px-4 py-8">
            <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
              <div className="mb-6">
                <div className="w-16 h-16 mx-auto bg-yellow-100 rounded-full flex items-center justify-center">
                  <AlertCircle className="w-8 h-8 text-yellow-500" />
                </div>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-3">無可用數據</h1>
              <p className="text-gray-600 mb-6">目前沒有可顯示的分析數據</p>
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-2.5 bg-sky-500 text-white rounded-lg hover:bg-sky-600 transition-colors font-medium"
              >
                重新載入
              </button>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <div className={styles.container}>
      <h1>Analytics Dashboard</h1>
      <div>
        <h2>Overview</h2>
        <p>Total Events: {logData.totalEvents}</p>
        <p>Unique Users: {logData.uniqueUsers}</p>
      </div>
      <div>
        <h2>Top Categories</h2>
        <ul>
          {logData.topCategories.map((category) => (
            <li key={category}>{category}</li>
          ))}
        </ul>
      </div>
      <div>
        <h2>Top Searches</h2>
        <ul>
          {logData.topSearches.map((search) => (
            <li key={search.query}>{search.query} ({search.count})</li>
          ))}
        </ul>
      </div>
      <div>
        <h2>Top Clicked Products</h2>
        <ul>
          {logData.topClicks.map((click) => (
            <li key={click.product}>{click.product} ({click.count})</li>
          ))}
        </ul>
      </div>
      <div>
        <h2>Hourly Activity</h2>
        <ul>
          {logData.hourlyTimeline.map((hour) => (
            <li key={hour.hour}>{hour.hour}: {hour.count}</li>
          ))}
        </ul>
      </div>
      <div>
        <h2>Recent Activity</h2>
        <ul>
          {logData.recentActivity.map((activity, index) => (
            <li key={index}>{activity.timestamp}: {activity.action}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

export default AnalyticsPage;

