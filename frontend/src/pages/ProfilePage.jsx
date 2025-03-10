import React, { useState } from "react";
import ViewProfile from "../Profile/ViewProfile";
import EditProfile from "../Profile/EditProfile";
import { Box, Tabs, Tab, Typography, Button, Paper, Avatar, List, ListItem, ListItemText } from "@mui/material";

const ProfilePage = () => {
  const [tab, setTab] = useState(0);
  const [recentActivities, setRecentActivities] = useState([
    "Updated resume",
    "Applied to 2 new jobs",
    "Edited profile details",
  ]);

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
  };

  return (
    <Box sx={{ padding: 4 }}>
      <Typography variant="h4" sx={{ mb: 3 }}>
        My Profile
      </Typography>
      <Tabs value={tab} onChange={handleTabChange} indicatorColor="primary" textColor="primary">
        <Tab label="View Profile" />
        <Tab label="Edit Profile" />
        <Tab label="Recent Activities" />
      </Tabs>

      <Box sx={{ mt: 3 }}>
        {tab === 0 && <ViewProfile />}
        {tab === 1 && <EditProfile />}
        {tab === 2 && (
          <Paper elevation={3} sx={{ padding: 3 }}>
            <Typography variant="h6">Recent Activities</Typography>
            <List>
              {recentActivities.map((activity, index) => (
                <ListItem key={index}>
                  <ListItemText primary={activity} />
                </ListItem>
              ))}
            </List>
            <Button variant="contained" color="primary" sx={{ mt: 2 }}>
              Clear Activities
            </Button>
          </Paper>
        )}
      </Box>

      {/* Profile Completion Widget */}
      <Paper elevation={3} sx={{ padding: 3, mt: 3 }}>
        <Typography variant="h6" sx={{ mb: 2 }}>
          Profile Completion
        </Typography>
        <Box
          sx={{
            display: "flex",
            alignItems: "center",
          }}
        >
          <Avatar sx={{ backgroundColor: "#4caf50", color: "#fff", mr: 2 }}>80%</Avatar>
          <Typography>Your profile is 80% complete. Complete all sections for better visibility.</Typography>
        </Box>
        <Button variant="outlined" color="secondary" sx={{ mt: 2 }}>
          Complete Now
        </Button>
      </Paper>
    </Box>
  );
};

export default ProfilePage;
