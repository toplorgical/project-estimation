
import React from "react";
import ProfileForm from "@/components/profile/ProfileForm";

const Profile: React.FC = () => {
  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">User Profile</h1>
      <ProfileForm />
    </div>
  );
};

export default Profile;
