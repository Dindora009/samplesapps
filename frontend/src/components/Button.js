import React from 'react';

const Button = ({ 
  children, 
  onClick, 
  variant = 'primary', 
  size = 'md',
  disabled = false,
  fullWidth = false,
  type = 'button',
  className = ''
}) => {
  const baseStyles = "rounded font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200";
  
  const variants = {
    primary: "bg-primary hover:bg-primary-light text-white focus:ring-primary-light",
    secondary: "bg-secondary hover:bg-secondary-light text-white focus:ring-secondary-light",
    accent: "bg-accent hover:bg-accent-light text-white focus:ring-accent-light",
    outline: "bg-transparent border border-primary text-primary hover:bg-primary hover:text-white focus:ring-primary-light",
    ghost: "bg-transparent text-primary hover:bg-primary-light/10 focus:ring-primary-light/30"
  };
  
  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-2.5 text-lg"
  };
  
  const disabledStyles = disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer";
  const widthStyles = fullWidth ? "w-full" : "";
  
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${disabledStyles} ${widthStyles} ${className}`}
    >
      {children}
    </button>
  );
};

export default Button;
