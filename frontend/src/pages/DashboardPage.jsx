import React, { useState } from "react";
import Dashboard from "../Dashboard/Dashboard";
import { Box, Typography, Grid, Paper, Switch, TextField, Button } from "@mui/material";
import NotificationsActiveIcon from "@mui/icons-material/NotificationsActive";

const DashboardPage = () => {
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [jobSearchTerm, setJobSearchTerm] = useState("");
  const [jobSuggestions, setJobSuggestions] = useState([]);

  const handleNotificationToggle = () => {
    setNotificationsEnabled(!notificationsEnabled);
  };

  const handleJobSearch = () => {
    // Mock job search functionality
    const mockJobs = [
      "Frontend Developer at TechCorp",
      "Data Engineer at AnalyticsHub",
      "Full Stack Developer at InnovateX",
    ];
    setJobSuggestions(mockJobs.filter((job) => job.toLowerCase().includes(jobSearchTerm.toLowerCase())));
  };

  return (
    <Box sx={{ padding: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        Dashboard
      </Typography>
      <Grid container spacing={4}>
        {/* Main Dashboard Content */}
        <Grid item xs={12} md={8}>
          <Dashboard />
        </Grid>

        {/* Notifications & Job Search */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ padding: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Notifications
            </Typography>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                mb: 2,
              }}
            >
              <Typography>Enable Notifications</Typography>
              <Switch
                checked={notificationsEnabled}
                onChange={handleNotificationToggle}
                color="primary"
              />
            </Box>
            {notificationsEnabled && (
              <Box sx={{ display: "flex", alignItems: "center", mt: 2 }}>
                <NotificationsActiveIcon sx={{ color: "#f57c00", mr: 2 }} />
                <Typography variant="body1">You have 3 new notifications.</Typography>
              </Box>
            )}
          </Paper>
          <Paper elevation={3} sx={{ padding: 3, mt: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Quick Job Search
            </Typography>
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Search for jobs..."
              value={jobSearchTerm}
              onChange={(e) => setJobSearchTerm(e.target.value)}
              sx={{ mb: 2 }}
            />
            <Button variant="contained" color="primary" onClick={handleJobSearch}>
              Search
            </Button>
            {jobSuggestions.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle1">Suggestions:</Typography>
                {jobSuggestions.map((job, index) => (
                  <Typography key={index} variant="body2" sx={{ mt: 1 }}>
                    {job}
                  </Typography>
                ))}
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage;
