"use client";
import React, { useState, useEffect } from "react";
import "./Login.css";
import axios from "axios";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

import { useNavigate } from "react-router-dom";

export default function Login() {
  const [isLogin, setIsLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [particles, setParticles] = useState([]);
  const [isTransitioning, setIsTransitioning] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    if (errors[name]) {
      setErrors((prev) => ({
        ...prev,
        [name]: "",
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Email is invalid";
    }

    if (!formData.password) {
      newErrors.password = "Password is required";
    } else if (formData.password.length < 6) {
      newErrors.password = "Password must be at least 6 characters";
    }

    if (!isLogin) {
      if (!formData.name) {
        newErrors.name = "Name is required";
      }
      if (!formData.confirmPassword) {
        newErrors.confirmPassword = "Please confirm your password";
      } else if (formData.password !== formData.confirmPassword) {
        newErrors.confirmPassword = "Passwords do not match";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setIsLoading(true);

    const url = isLogin
      ? "http://localhost:5000/login"
      : "http://localhost:5000/signup";

    const payload = {
      email: formData.email,
      password: formData.password,
      ...(isLogin ? {} : { name: formData.name }), // only send name in signup
    };

    try {
      const res = await axios.post(url, payload);

      toast.success(res.data.message);

      if (isLogin) {
        setTimeout(() => {
          navigate("/home");
        }, 2000);
      } else {
        setTimeout(() => {
          setIsLogin(true);
          toggleMode();
        }, 2000);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || ("Something went wrong!" , err);
      toast.error(errorMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleMode = () => {
    setIsTransitioning(true);

    setTimeout(() => {
      setIsLogin(!isLogin);
      setFormData({
        name: "",
        email: "",
        password: "",
        confirmPassword: "",
      });
      setErrors({});
      setIsTransitioning(false);
    }, 300);
  };

  useEffect(() => {
    const generateParticles = () => {
      const newParticles = [];
      for (let i = 0; i < 20; i++) {
        newParticles.push({
          id: i,
          x: Math.random() * 100,
          y: Math.random() * 100,
          delay: Math.random() * 5,
        });
      }
      setParticles(newParticles);
    };
    generateParticles();
  }, []);

  return (
    <div className="auth-container">
      <ToastContainer />
      <div className="auth-background">
        <div className="floating-shapes">
          <div className="shape shape-1"></div>
          <div className="shape shape-2"></div>
          <div className="shape shape-3"></div>
          <div className="shape shape-4"></div>
          <div className="shape shape-5"></div>
          <div className="shape shape-6"></div>

          <div className="particles">
            {particles.map((particle) => (
              <div
                key={particle.id}
                className="particle"
                style={{
                  left: `${particle.x}%`,
                  top: `${particle.y}%`,
                  animationDelay: `${particle.delay}s`,
                }}
              />
            ))}
          </div>

          <div className="animated-grid">
            {Array.from({ length: 100 }).map((_, i) => (
              <div key={i} className="grid-dot" />
            ))}
          </div>
        </div>
      </div>

      <div className={`auth-card ${isTransitioning ? "transitioning" : ""}`}>
        <div className="card-glow"></div>
        <div className="auth-header">
          <div className="title-container">
            <h1 className="auth-title">
              {isLogin ? "Welcome Back" : "Create Account"}
            </h1>
            <div className="title-underline"></div>
          </div>
          <p className="auth-subtitle">
            {isLogin
              ? "Sign in to your account to continue"
              : "Join us today and get started"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          {!isLogin && (
            <div className="form-group">
              <label htmlFor="name" className="form-label">
                Full Name
              </label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                className={`form-input ${errors.name ? "error" : ""}`}
                placeholder="Enter your full name"
              />
              {errors.name && (
                <span className="error-message">{errors.name}</span>
              )}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={`form-input ${errors.email ? "error" : ""}`}
              placeholder="Enter your email"
            />
            {errors.email && (
              <span className="error-message">{errors.email}</span>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleInputChange}
              className={`form-input ${errors.password ? "error" : ""}`}
              placeholder="Enter your password"
            />
            {errors.password && (
              <span className="error-message">{errors.password}</span>
            )}
          </div>

          {!isLogin && (
            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label">
                Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                className={`form-input ${
                  errors.confirmPassword ? "error" : ""
                }`}
                placeholder="Confirm your password"
              />
              {errors.confirmPassword && (
                <span className="error-message">{errors.confirmPassword}</span>
              )}
            </div>
          )}

          <button type="submit" className="submit-button" disabled={isLoading}>
            {isLoading ? (
              <div className="loading-container">
                <div className="loading-spinner-advanced">
                  <div className="spinner-ring"></div>
                  <div className="spinner-ring"></div>
                  <div className="spinner-ring"></div>
                </div>
                {isLogin ? <span>Login...</span> : <span>Creating...</span>}

                <div className="loading-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            ) : (
              <>
                <span className="button-text">
                  {isLogin ? "Sign In" : "Create Account"}
                </span>
                <div className="button-ripple"></div>
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p className="toggle-text">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <button
              type="button"
              onClick={toggleMode}
              className="toggle-button"
            >
              {isLogin ? "Sign Up" : "Sign In"}
            </button>
          </p>
        </div>

        {isLoading && (
          <div className="db-animation-advanced">
            <div className="server-rack">
              <div className="server server-1">
                <div className="server-lights">
                  <div className="light"></div>
                  <div className="light"></div>
                  <div className="light"></div>
                </div>
              </div>
              <div className="server server-2">
                <div className="server-lights">
                  <div className="light"></div>
                  <div className="light"></div>
                  <div className="light"></div>
                </div>
              </div>
              <div className="server server-3">
                <div className="server-lights">
                  <div className="light"></div>
                  <div className="light"></div>
                  <div className="light"></div>
                </div>
              </div>
            </div>
            <div className="data-flow">
              <div className="data-packet"></div>
              <div className="data-packet"></div>
              <div className="data-packet"></div>
            </div>
            <div className="connection-status">
              <div className="status-indicator"></div>
              <span>Authenticating...</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
