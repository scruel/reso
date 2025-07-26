import { FC, useEffect, useState } from "react";
import axios from "axios";
import styles from "./AnalyticsPage.module.css";

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

  useEffect(() => {
    const fetchLogData = async () => {
      try {
        const response = await axios.get("/api/analytics");
        setLogData(response.data);
      } catch (error) {
        console.error("Error fetching analytics data", error);
      }
    };

    fetchLogData();
  }, []);

  if (!logData) {
    return <div>Loading...</div>;
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

