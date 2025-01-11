import React, { useState, useEffect } from 'react';
import './Dashboard.css';
import {
  Box,
  Typography,
  Paper,
  Grid,
  CircularProgress,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Timeline,
  Person,
  Business,
  WorkOutline,
  TrendingUp,
  Assessment
} from '@mui/icons-material';

const Dashboard = () => {
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    applications: 0,
    interviews: 0,
    connections: 0,
    profileViews: 0
  });

  // Simulating data loading
  useEffect(() => {
    const fetchData = async () => {
      // Simulated API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      setStats({
        applications: 42,
        interviews: 8,
        connections: 150,
        profileViews: 324
      });
      setIsLoading(false);
    };

    fetchData();
  }, []);

  const recentActivities = [
    {
      title: "Application Submitted",
      company: "TechCorp",
      position: "Senior Frontend Developer",
      date: "2 hours ago",
      icon: <WorkOutline />
    },
    {
      title: "Profile Updated",
      description: "Added new skills and projects",
      date: "1 day ago",
      icon: <Person />
    },
    {
      title: "New Connection",
      company: "InnovateX",
      description: "Connected with Technical Recruiter",
      date: "2 days ago",
      icon: <Business />
    }
  ];

  const StatsCard = ({ title, value, icon }) => (
    <Card className="stats-card dashboard-paper">
      <CardContent>
        <Box className="stats-content">
          {icon}
          <Box className="stats-details">
            <Typography variant="h6" className="stats-value">
              {value}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              {title}
            </Typography>
          </Box>
        </Box>
      </CardContent>
    </Card>
  );

  if (isLoading) {
    return (
      <Box className="loading-container">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box className="dashboard-main">
      {/* Stats Section */}
      <Grid container spacing={3} className="stats-grid">
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Applications"
            value={stats.applications}
            icon={<Assessment className="stats-icon" />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Interviews"
            value={stats.interviews}
            icon={<Timeline className="stats-icon" />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Connections"
            value={stats.connections}
            icon={<Person className="stats-icon" />}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Profile Views"
            value={stats.profileViews}
            icon={<TrendingUp className="stats-icon" />}
          />
        </Grid>
      </Grid>

      {/* Activity Timeline */}
      <Paper elevation={3} className="dashboard-paper activity-section">
        <Typography variant="h6" className="section-title">
          Recent Activity
        </Typography>
        <List>
          {recentActivities.map((activity, index) => (
            <ListItem key={index} className="activity-item">
              <ListItemIcon className="activity-icon">
                {activity.icon}
              </ListItemIcon>
              <ListItemText
                primary={activity.title}
                secondary={
                  <React.Fragment>
                    {activity.company && (
                      <Typography component="span" className="company-name">
                        {activity.company}
                        {activity.position && ` - ${activity.position}`}
                      </Typography>
                    )}
                    {activity.description && (
                      <Typography component="p" className="activity-description">
                        {activity.description}
                      </Typography>
                    )}
                    <Typography component="span" className="activity-date">
                      {activity.date}
                    </Typography>
                  </React.Fragment>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
};

export default Dashboard;
