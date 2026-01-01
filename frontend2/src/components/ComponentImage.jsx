import React, { useState, useEffect } from "react";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const PLACEHOLDER_PATH = "/placeholder.svg";

/**
 * ComponentImage - Safely displays component images with placeholder fallback
 * Prevents infinite loops and flashing by checking image_path validity before loading
 */
export default function ComponentImage({ 
  imagePath, 
  alt = "Component", 
  className = "", 
  style = {},
  ...props 
}) {
  const [imageSrc, setImageSrc] = useState(null);
  const [hasError, setHasError] = useState(false);

  useEffect(() => {
    // Reset error state when imagePath changes
    setHasError(false);
    
    // Check if imagePath is valid
    if (!imagePath || imagePath === "null" || imagePath === "undefined" || imagePath.trim() === "") {
      // No valid image path, use placeholder directly
      setImageSrc(PLACEHOLDER_PATH);
    } else {
      // Valid image path, try to load it
      setImageSrc(`${API_BASE}/${imagePath}`);
    }
  }, [imagePath]);

  const handleError = (e) => {
    // Prevent infinite loop by checking if we're already showing placeholder
    if (e.currentTarget.src !== PLACEHOLDER_PATH && !hasError) {
      setHasError(true);
      setImageSrc(PLACEHOLDER_PATH);
    }
  };

  // If no src is set yet, show placeholder immediately
  const finalSrc = imageSrc || PLACEHOLDER_PATH;

  return (
    <img
      src={finalSrc}
      alt={alt}
      className={className}
      style={style}
      onError={handleError}
      {...props}
    />
  );
}

