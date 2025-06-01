'use client';

import Image from 'next/image';

interface ProfileImageProps {
  profilePhoto?: string | null;
  gender: string;
  firstName: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const defaultImages = {
  'M': '/avatars/male-avatar.svg',
  'F': '/avatars/female-avatar.svg',
  'O': '/avatars/other-avatar.svg'
};

const sizes = {
  sm: { width: 32, height: 32, textSize: 'text-sm' },
  md: { width: 64, height: 64, textSize: 'text-xl' },
  lg: { width: 128, height: 128, textSize: 'text-4xl' }
};

export default function ProfileImage({ profilePhoto, gender, firstName, size = 'sm', className = '' }: ProfileImageProps) {
  const { width, height, textSize } = sizes[size];
  
  if (profilePhoto) {
    return (
      <Image
        src={profilePhoto}
        alt="Profile"
        width={width}
        height={height}
        className={`rounded-full object-cover ${className}`}
      />
    );
  }

  if (gender in defaultImages) {
    return (
      <Image
        src={defaultImages[gender as keyof typeof defaultImages]}
        alt={`${gender} Avatar`}
        width={width}
        height={height}
        className={`rounded-full object-cover ${className}`}
        priority
      />
    );
  }

  // Fallback to initials if no photo and no default image
  return (
    <div 
      className={`h-${height} w-${width} rounded-full bg-blue-100 flex items-center justify-center text-blue-600 ${textSize} font-semibold ${className}`}
    >
      {firstName[0]}
    </div>
  );
} 