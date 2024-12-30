import React from "react";
import { Box, Grid, Paper, Typography, Avatar, Button } from "@mui/material";
import TaskIcon from "@mui/icons-material/Task";
import PieChartIcon from "@mui/icons-material/PieChart";
import RecentActorsIcon from "@mui/icons-material/RecentActors";

const Dashboard = () => {
  const userName = "John Doe";

  return (
    <Box sx={{ padding: 4, backgroundColor: "#f9f9f9", minHeight: "100vh" }}>
      <Typography variant="h4" sx={{ mb: 4 }}>
        Welcome, {userName}
      </Typography>
      <Grid container spacing={4}>
        {/* Profile Widget */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ padding: 3, textAlign: "center" }}>
            <Avatar sx={{ width: 80, height: 80, margin: "auto" }} />
            <Typography variant="h6" sx={{ mt: 2 }}>
              {userName}
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Full Stack Developer
            </Typography>
            <Button variant="contained" color="primary" sx={{ mt: 2 }}>
              Edit Profile
            </Button>
          </Paper>
        </Grid>

        {/* Resume Widget */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ padding: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Resume Status
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <TaskIcon sx={{ fontSize: 40, color: "#4caf50", mr: 2 }} />
              <Typography variant="body1">Your resume is up to date!</Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Insights Widget */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ padding: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Insights
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <PieChartIcon sx={{ fontSize: 40, color: "#2196f3", mr: 2 }} />
              <Typography variant="body1">
                You've applied to 10 jobs this month.
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Recent Activities */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ padding: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Recent Activities
            </Typography>
            <Box sx={{ display: "flex", alignItems: "center" }}>
              <RecentActorsIcon sx={{ fontSize: 40, color: "#ff5722", mr: 2 }} />
              <Typography variant="body1">Viewed 15 job postings recently.</Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Dashboard;
