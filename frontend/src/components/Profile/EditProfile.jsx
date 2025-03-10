import React, { useState, useEffect } from "react";
import axios from "../../services/api";

const EditProfile = () => {
  const [profile, setProfile] = useState({
    preferred_job_title: "",
    bio: "",
    linkedin_profile: "",
    github_profile: "",
    portfolio_website: "",
    location: "",
    years_of_experience: "",
    experience_level: "ENTRY",
    employment_status: "ACTIVE",
    remote_work_preference: "FLEXIBLE",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProfile({ ...profile, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.put("/api/profile/", profile);
      alert("Profile updated successfully!");
    } catch (error) {
      console.error("Error updating profile:", error);
    }
  };

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

  return (
    <form onSubmit={handleSubmit} className="edit-profile-form">
      <h2>Edit Your Profile</h2>
      <label>
        Job Title:
        <input
          type="text"
          name="preferred_job_title"
          value={profile.preferred_job_title}
          onChange={handleChange}
        />
      </label>
      <label>
        Bio:
        <textarea
          name="bio"
          value={profile.bio}
          onChange={handleChange}
        ></textarea>
      </label>
      <label>
        LinkedIn Profile:
        <input
          type="url"
          name="linkedin_profile"
          value={profile.linkedin_profile}
          onChange={handleChange}
        />
      </label>
      <label>
        GitHub Profile:
        <input
          type="url"
          name="github_profile"
          value={profile.github_profile}
          onChange={handleChange}
        />
      </label>
      <label>
        Portfolio Website:
        <input
          type="url"
          name="portfolio_website"
          value={profile.portfolio_website}
          onChange={handleChange}
        />
      </label>
      <label>
        Location:
        <input
          type="text"
          name="location"
          value={profile.location}
          onChange={handleChange}
        />
      </label>
      <label>
        Years of Experience:
        <input
          type="number"
          name="years_of_experience"
          value={profile.years_of_experience}
          onChange={handleChange}
        />
      </label>
      <label>
        Experience Level:
        <select
          name="experience_level"
          value={profile.experience_level}
          onChange={handleChange}
        >
          <option value="ENTRY">Entry Level</option>
          <option value="MID">Mid Level</option>
          <option value="SENIOR">Senior Level</option>
          <option value="LEAD">Team Lead</option>
          <option value="EXECUTIVE">Executive</option>
        </select>
      </label>
      <label>
        Employment Status:
        <select
          name="employment_status"
          value={profile.employment_status}
          onChange={handleChange}
        >
          <option value="ACTIVE">Actively Looking</option>
          <option value="PASSIVE">Open to Opportunities</option>
          <option value="EMPLOYED">Not Looking</option>
        </select>
      </label>
      <label>
        Remote Work Preference:
        <select
          name="remote_work_preference"
          value={profile.remote_work_preference}
          onChange={handleChange}
        >
          <option value="ONSITE">On-site only</option>
          <option value="HYBRID">Hybrid preferred</option>
          <option value="REMOTE">Remote only</option>
          <option value="FLEXIBLE">Flexible</option>
        </select>
      </label>
      <button type="submit">Save Changes</button>
    </form>
  );
};

export default EditProfile;
