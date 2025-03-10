import React, { useState, useEffect } from "react";
import axios from "../../services/api";

const ViewProfile = () => {
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const { data } = await axios.get("/api/profile/");
        setProfile(data);
      } catch (error) {
        console.error("Error fetching profile:", error);
      }
    };
    fetchProfile();
  }, []);

  if (!profile) return <p>Loading profile...</p>;

  return (
    <div className="view-profile">
      <h1>{profile.user?.full_name || profile.user?.username}'s Profile</h1>
      <p><strong>Job Title:</strong> {profile.preferred_job_title}</p>
      <p><strong>Bio:</strong> {profile.bio}</p>
      <p><strong>Years of Experience:</strong> {profile.years_of_experience}</p>
      <p><strong>Experience Level:</strong> {profile.experience_level}</p>
      <p><strong>Employment Status:</strong> {profile.employment_status}</p>
      <p><strong>Location:</strong> {profile.location}</p>
      <p><strong>Remote Work Preference:</strong> {profile.remote_work_preference}</p>
      {profile.linkedin_profile && (
        <p><strong>LinkedIn:</strong> <a href={profile.linkedin_profile} target="_blank" rel="noopener noreferrer">{profile.linkedin_profile}</a></p>
      )}
      {profile.github_profile && (
        <p><strong>GitHub:</strong> <a href={profile.github_profile} target="_blank" rel="noopener noreferrer">{profile.github_profile}</a></p>
      )}
      {profile.portfolio_website && (
        <p><strong>Portfolio:</strong> <a href={profile.portfolio_website} target="_blank" rel="noopener noreferrer">{profile.portfolio_website}</a></p>
      )}
      {profile.resume_file && (
        <p><strong>Resume:</strong> <a href={profile.resume_file} target="_blank" rel="noopener noreferrer">Download Resume</a></p>
      )}
    </div>
  );
};

export default ViewProfile;
