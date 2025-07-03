import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Context for user management
const UserContext = createContext();

const UserProvider = ({ children }) => {
  const [currentUser, setCurrentUser] = useState(null);
  const [userType, setUserType] = useState(null); // 'customer', 'business', 'admin'

  return (
    <UserContext.Provider value={{ currentUser, setCurrentUser, userType, setUserType }}>
      {children}
    </UserContext.Provider>
  );
};

const useUser = () => useContext(UserContext);

// Demo User Selector Component
const DemoUserSelector = ({ onUserSelect }) => {
  const [demoUsers, setDemoUsers] = useState(null);

  useEffect(() => {
    fetchDemoUsers();
  }, []);

  const fetchDemoUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/demo-users`);
      setDemoUsers(response.data);
    } catch (error) {
      console.error("Error fetching demo users:", error);
    }
  };

  if (!demoUsers) return <div>Loading demo users...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
          Demo Platform Access
        </h2>
        <p className="text-gray-600 mb-8 text-center">
          Choose a demo account to explore ImpactLink's features
        </p>

        <div className="grid md:grid-cols-3 gap-6">
          {/* Demo Business */}
          {demoUsers.demo_business && (
            <div className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition-all">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">🏢</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-800">Demo Business</h3>
                <p className="text-gray-600">{demoUsers.demo_business.name}</p>
              </div>
              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <p><strong>Industry:</strong> {demoUsers.demo_business.industry}</p>
                <p><strong>Account:</strong> {demoUsers.demo_business.account_number}</p>
                <p><strong>Impact:</strong> ${demoUsers.demo_business.total_impact.toFixed(0)}</p>
              </div>
              <button
                onClick={() => onUserSelect(demoUsers.demo_business, 'business')}
                className="w-full bg-blue-500 text-white py-2 rounded-lg hover:bg-blue-600 transition-all"
              >
                Login as Business
              </button>
            </div>
          )}

          {/* Demo Customer */}
          {demoUsers.demo_customer && (
            <div className="border border-gray-200 rounded-lg p-6 hover:border-green-300 transition-all">
              <div className="text-center mb-4">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                  <span className="text-2xl">👤</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-800">Demo Customer</h3>
                <p className="text-gray-600">{demoUsers.demo_customer.name}</p>
              </div>
              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <p><strong>Email:</strong> {demoUsers.demo_customer.email}</p>
                <p><strong>Account:</strong> {demoUsers.demo_customer.account_number}</p>
                <p><strong>Donated:</strong> ${demoUsers.demo_customer.total_contributions.toFixed(0)}</p>
              </div>
              <button
                onClick={() => onUserSelect(demoUsers.demo_customer, 'customer')}
                className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition-all"
              >
                Login as Customer
              </button>
            </div>
          )}

          {/* Demo Admin */}
          <div className="border border-gray-200 rounded-lg p-6 hover:border-purple-300 transition-all">
            <div className="text-center mb-4">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-2xl">⚙️</span>
              </div>
              <h3 className="text-xl font-semibold text-gray-800">Demo Admin</h3>
              <p className="text-gray-600">Platform Administrator</p>
            </div>
            <div className="space-y-2 text-sm text-gray-600 mb-4">
              <p><strong>Role:</strong> System Admin</p>
              <p><strong>Access:</strong> Full Platform</p>
              <p><strong>Features:</strong> All Management Tools</p>
            </div>
            <button
              onClick={() => onUserSelect({ username: 'demo_admin', role: 'admin' }, 'admin')}
              className="w-full bg-purple-500 text-white py-2 rounded-lg hover:bg-purple-600 transition-all"
            >
              Login as Admin
            </button>
          </div>
        </div>

        <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-semibold text-blue-800 mb-2">Demo Instructions:</h4>
          <ul className="text-blue-700 text-sm space-y-1">
            <li>• <strong>Business Demo:</strong> Create transactions, manage cause allocations, view impact dashboard</li>
            <li>• <strong>Customer Demo:</strong> Make donations, set cause preferences, view contribution history</li>
            <li>• <strong>Admin Demo:</strong> Manage platform, verify businesses, monitor all activities</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

// Enhanced Cause Browser Component with Filtering and Expiry
const CauseBrowser = () => {
  const [causes, setCauses] = useState([]);
  const [filteredCauses, setFilteredCauses] = useState([]);
  const [selectedCause, setSelectedCause] = useState(null);
  const [filters, setFilters] = useState({
    category: "",
    expired: null,
    sort_by: "created_at",
    sort_order: "desc"
  });
  const [donationAmount, setDonationAmount] = useState("");
  const [message, setMessage] = useState("");
  const [paymentMethod, setPaymentMethod] = useState(null);
  const [isAnonymous, setIsAnonymous] = useState(false);
  const [anonymousName, setAnonymousName] = useState("");
  const [anonymousEmail, setAnonymousEmail] = useState("");
  
  // Social features state
  const [showComments, setShowComments] = useState({});
  const [comments, setComments] = useState({});
  const [reactions, setReactions] = useState({});
  const [newComment, setNewComment] = useState("");
  const [replyTo, setReplyTo] = useState(null);
  
  const { currentUser, userType } = useUser();

  useEffect(() => {
    fetchCauses();
  }, [filters]);

  const fetchCauses = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.category) params.append('category', filters.category);
      if (filters.expired !== null) params.append('expired', filters.expired);
      params.append('sort_by', filters.sort_by);
      params.append('sort_order', filters.sort_order);
      params.append('active_only', 'false'); // Show all causes including expired

      const response = await axios.get(`${API}/causes?${params}`);
      setCauses(response.data);
      setFilteredCauses(response.data);
      
      // Fetch reactions for all causes
      for (const cause of response.data) {
        fetchCauseReactions(cause.id);
      }
    } catch (error) {
      console.error("Error fetching causes:", error);
    }
  };

  // Social features functions
  const fetchCauseReactions = async (causeId) => {
    try {
      const response = await axios.get(`${API}/causes/${causeId}/reactions`);
      setReactions(prev => ({
        ...prev,
        [causeId]: response.data
      }));
    } catch (error) {
      console.error("Error fetching reactions:", error);
    }
  };

  const fetchCauseComments = async (causeId) => {
    try {
      const response = await axios.get(`${API}/causes/${causeId}/comments`);
      setComments(prev => ({
        ...prev,
        [causeId]: response.data
      }));
    } catch (error) {
      console.error("Error fetching comments:", error);
    }
  };

  const addReaction = async (causeId, emoji) => {
    if (!currentUser) {
      alert("Please log in to react to causes");
      return;
    }

    try {
      await axios.post(`${API}/causes/${causeId}/reactions?user_id=${currentUser.id}&user_type=${userType}`, {
        emoji: emoji
      });
      fetchCauseReactions(causeId);
    } catch (error) {
      console.error("Error adding reaction:", error);
    }
  };

  const removeReaction = async (causeId) => {
    if (!currentUser) return;

    try {
      await axios.delete(`${API}/causes/${causeId}/reactions?user_id=${currentUser.id}`);
      fetchCauseReactions(causeId);
    } catch (error) {
      console.error("Error removing reaction:", error);
    }
  };

  const addComment = async (causeId, commentText, parentId = null) => {
    if (!currentUser) {
      alert("Please log in to comment");
      return;
    }

    if (!commentText.trim()) return;

    try {
      await axios.post(`${API}/causes/${causeId}/comments?user_id=${currentUser.id}&user_type=${userType}`, {
        comment: commentText,
        parent_comment_id: parentId
      });
      
      setNewComment("");
      setReplyTo(null);
      fetchCauseComments(causeId);
    } catch (error) {
      console.error("Error adding comment:", error);
    }
  };

  const shareCause = async (causeId, platform = 'link') => {
    try {
      const response = await axios.get(`${API}/causes/${causeId}/share`);
      const shareData = response.data;
      
      if (platform === 'copy') {
        navigator.clipboard.writeText(shareData.share_url);
        alert("Link copied to clipboard!");
      } else if (platform === 'link') {
        // Just copy the link
        navigator.clipboard.writeText(shareData.share_url);
        alert("Share link copied to clipboard!");
      } else {
        // Open social platform
        window.open(shareData.social_links[platform], '_blank');
      }

      // Track share
      if (currentUser) {
        await axios.post(`${API}/causes/${causeId}/share`, {
          user_id: currentUser.id,
          platform: platform
        });
      }
    } catch (error) {
      console.error("Error sharing cause:", error);
    }
  };

  const toggleComments = (causeId) => {
    setShowComments(prev => ({
      ...prev,
      [causeId]: !prev[causeId]
    }));
    
    if (!comments[causeId]) {
      fetchCauseComments(causeId);
    }
  };



  const handleDonate = async () => {
    if (!paymentMethod) {
      alert("Please select a payment method");
      return;
    }

    if (!currentUser && (!anonymousName || !anonymousEmail)) {
      alert("Please provide your name and email for anonymous donation");
      return;
    }

    try {
      const contributionData = {
        cause_id: selectedCause.id,
        amount: parseFloat(donationAmount),
        payment_method: paymentMethod,
        message: message || undefined,
        anonymous: isAnonymous
      };

      if (currentUser) {
        contributionData.customer_id = currentUser.id;
      } else {
        contributionData.customer_name = anonymousName;
        contributionData.customer_email = anonymousEmail;
      }

      await axios.post(`${API}/contributions`, contributionData);
      alert(`Thank you! Your $${donationAmount} donation will help ${selectedCause.name}`);
      setSelectedCause(null);
      setDonationAmount("");
      setMessage("");
      setPaymentMethod(null);
      setAnonymousName("");
      setAnonymousEmail("");
      fetchCauses(); // Refresh to show updated totals
    } catch (error) {
      console.error("Error making donation:", error);
      alert("Error processing donation: " + (error.response?.data?.detail || error.message));
    }
  };

  const getCauseProgress = (cause) => {
    if (!cause.goal_amount) return 0;
    return Math.min((cause.total_raised / cause.goal_amount) * 100, 100);
  };

  const getCategoryColor = (category) => {
    const colors = {
      "Education": "bg-blue-500",
      "Health": "bg-red-500",
      "Environment": "bg-green-500",
      "Poverty": "bg-yellow-500",
      "default": "bg-gray-500"
    };
    return colors[category] || colors.default;
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getDaysRemaining = (endDate) => {
    if (!endDate) return null;
    const end = new Date(endDate);
    const now = new Date();
    const diffTime = end - now;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  };

  const getPaymentMethodBadges = (methods) => {
    const badges = {
      card: { icon: "💳", color: "bg-blue-100 text-blue-800" },
      momo: { icon: "📱", color: "bg-green-100 text-green-800" },
      papss: { icon: "🏦", color: "bg-purple-100 text-purple-800" },
      bank_transfer: { icon: "🏧", color: "bg-gray-100 text-gray-800" }
    };

    return methods.map(method => badges[method] || { icon: "💰", color: "bg-gray-100 text-gray-800" });
  };

  const categories = ["Education", "Health", "Environment", "Poverty"];

  return (
    <div className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Support a Cause You Care About
          </h2>
          <p className="text-xl text-gray-600">
            Browse active and completed causes, filter by category, and make a direct impact
          </p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-xl shadow-lg p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Filter & Sort Causes</h3>
          <div className="grid md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
              <select
                value={filters.category}
                onChange={(e) => setFilters({...filters, category: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={filters.expired || ""}
                onChange={(e) => setFilters({...filters, expired: e.target.value === "" ? null : e.target.value === "true"})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Causes</option>
                <option value="false">Active Only</option>
                <option value="true">Expired Only</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Sort By</label>
              <select
                value={filters.sort_by}
                onChange={(e) => setFilters({...filters, sort_by: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="created_at">Most Recent</option>
                <option value="total_raised">Most Funded</option>
                <option value="end_date">Ending Soon</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Order</label>
              <select
                value={filters.sort_order}
                onChange={(e) => setFilters({...filters, sort_order: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                <option value="desc">Descending</option>
                <option value="asc">Ascending</option>
              </select>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredCauses.map((cause) => {
            const daysRemaining = getDaysRemaining(cause.end_date);
            const isExpiring = daysRemaining !== null && daysRemaining <= 7 && daysRemaining > 0;
            const isExpired = cause.expired || (daysRemaining !== null && daysRemaining <= 0);

            return (
              <div key={cause.id} className={`bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all ${isExpired ? 'opacity-75' : ''}`}>
                {cause.image_url && (
                  <img 
                    src={cause.image_url} 
                    alt={cause.name}
                    className="w-full h-48 object-cover"
                  />
                )}
                <div className="p-6">
                  <div className="flex items-center gap-2 mb-3">
                    <span className={`px-3 py-1 rounded-full text-white text-sm font-medium ${getCategoryColor(cause.category)}`}>
                      {cause.category}
                    </span>
                    {cause.featured && (
                      <span className="px-3 py-1 rounded-full bg-yellow-100 text-yellow-800 text-sm font-medium">
                        ⭐ Featured
                      </span>
                    )}
                    {isExpired && (
                      <span className="px-3 py-1 rounded-full bg-red-100 text-red-800 text-sm font-medium">
                        ❌ Expired
                      </span>
                    )}
                    {isExpiring && (
                      <span className="px-3 py-1 rounded-full bg-orange-100 text-orange-800 text-sm font-medium">
                        ⏰ Ending Soon
                      </span>
                    )}
                  </div>
                  
                  <h3 className="text-xl font-bold text-gray-800 mb-2">{cause.name}</h3>
                  <p className="text-gray-600 mb-4 text-sm">{cause.description}</p>
                  
                  {/* Creator Information */}
                  <div className="bg-gray-50 rounded-lg p-3 mb-4">
                    <p className="text-sm text-gray-600">
                      <strong>Created by:</strong> 
                      {cause.creator_website ? (
                        <a 
                          href={cause.creator_website} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 ml-1"
                        >
                          {cause.creator_name} 🔗
                        </a>
                      ) : (
                        <span className="ml-1">{cause.creator_name}</span>
                      )}
                      <span className="text-gray-500 ml-2">({cause.creator_type})</span>
                    </p>
                  </div>
                  
                  {/* Date Information */}
                  <div className="mb-4 text-sm text-gray-600">
                    <p><strong>Started:</strong> {formatDate(cause.start_date)}</p>
                    {cause.end_date && (
                      <p>
                        <strong>Ends:</strong> {formatDate(cause.end_date)}
                        {daysRemaining !== null && (
                          <span className={`ml-2 ${isExpiring ? 'text-orange-600' : isExpired ? 'text-red-600' : 'text-green-600'}`}>
                            ({daysRemaining > 0 ? `${daysRemaining} days left` : 'Ended'})
                          </span>
                        )}
                      </p>
                    )}
                  </div>
                  
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Progress</span>
                      <span>${cause.total_raised.toFixed(0)} raised</span>
                    </div>
                    {cause.goal_amount && (
                      <>
                        <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full transition-all" 
                            style={{ width: `${getCauseProgress(cause)}%` }}
                          ></div>
                        </div>
                        <div className="text-sm text-gray-600">
                          Goal: ${cause.goal_amount.toFixed(0)} ({getCauseProgress(cause).toFixed(1)}% reached)
                        </div>
                      </>
                    )}
                  </div>

                  <div className="mb-4">
                    <p className="text-sm text-gray-600 mb-2"><strong>Impact:</strong> ${cause.cost_per_impact} per {cause.impact_metric}</p>
                    <p className="text-sm text-gray-600 mb-3"><strong>Total Impact:</strong> {cause.total_impact_units.toFixed(0)} {cause.impact_metric}</p>
                    
                    <div className="flex flex-wrap gap-1 mb-3">
                      {getPaymentMethodBadges(cause.payment_methods_accepted).map((badge, index) => (
                        <span key={index} className={`px-2 py-1 rounded-full text-xs font-medium ${badge.color} flex items-center gap-1`}>
                          {badge.icon}
                        </span>
                      ))}
                    </div>

                    {/* Volunteer Opportunities */}
                    {cause.volunteer_opportunities && cause.volunteer_opportunities.length > 0 && (
                      <div className="mb-3">
                        <p className="text-sm text-gray-600 mb-1"><strong>Volunteer:</strong></p>
                        <div className="flex flex-wrap gap-1">
                          {cause.volunteer_opportunities.map((opportunity, index) => (
                            <span key={index} className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                              {opportunity.replace(/_/g, ' ')}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Social Features */}
                  <div className="border-t pt-4 mb-4">
                    {/* Emoji Reactions */}
                    <div className="flex items-center gap-2 mb-3">
                      <span className="text-sm text-gray-600 font-medium">React:</span>
                      {['❤️', '👍', '🎉', '😢', '😡'].map((emoji) => {
                        const isUserReaction = reactions[cause.id]?.user_reactions?.[currentUser?.id] === emoji;
                        const count = reactions[cause.id]?.reaction_counts?.[emoji] || 0;
                        
                        return (
                          <button
                            key={emoji}
                            onClick={() => isUserReaction ? removeReaction(cause.id) : addReaction(cause.id, emoji)}
                            className={`flex items-center gap-1 px-2 py-1 rounded-full text-sm transition-colors ${
                              isUserReaction 
                                ? 'bg-blue-100 text-blue-800 border-2 border-blue-300' 
                                : 'bg-gray-100 hover:bg-gray-200 text-gray-700'
                            }`}
                          >
                            <span>{emoji}</span>
                            {count > 0 && <span className="text-xs">{count}</span>}
                          </button>
                        );
                      })}
                    </div>

                    {/* Share and Comment Actions */}
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        {/* Share Button */}
                        <div className="relative group">
                          <button
                            onClick={() => shareCause(cause.id, 'copy')}
                            className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm hover:bg-green-200 transition-colors"
                          >
                            📤 Share
                          </button>
                          
                          {/* Share Dropdown */}
                          <div className="absolute bottom-full left-0 mb-2 hidden group-hover:block bg-white border border-gray-200 rounded-lg shadow-lg p-2 z-10">
                            <div className="flex gap-1">
                              <button
                                onClick={() => shareCause(cause.id, 'facebook')}
                                className="p-2 text-blue-600 hover:bg-blue-50 rounded"
                                title="Share on Facebook"
                              >
                                📘
                              </button>
                              <button
                                onClick={() => shareCause(cause.id, 'twitter')}
                                className="p-2 text-blue-400 hover:bg-blue-50 rounded"
                                title="Share on Twitter"
                              >
                                🐦
                              </button>
                              <button
                                onClick={() => shareCause(cause.id, 'whatsapp')}
                                className="p-2 text-green-600 hover:bg-green-50 rounded"
                                title="Share on WhatsApp"
                              >
                                📱
                              </button>
                              <button
                                onClick={() => shareCause(cause.id, 'copy')}
                                className="p-2 text-gray-600 hover:bg-gray-50 rounded"
                                title="Copy Link"
                              >
                                🔗
                              </button>
                            </div>
                          </div>
                        </div>

                        {/* Comments Toggle */}
                        <button
                          onClick={() => toggleComments(cause.id)}
                          className="flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm hover:bg-purple-200 transition-colors"
                        >
                          💬 Comments
                          {comments[cause.id] && (
                            <span className="text-xs">({comments[cause.id].total_comments})</span>
                          )}
                        </button>
                      </div>

                      <div className="text-xs text-gray-500">
                        {reactions[cause.id]?.total_reactions || 0} reactions
                      </div>
                    </div>

                    {/* Comments Section */}
                    {showComments[cause.id] && (
                      <div className="mt-4 border-t pt-3">
                        {/* Add Comment Form */}
                        {currentUser && (
                          <div className="mb-3">
                            <div className="flex gap-2">
                              <input
                                type="text"
                                value={replyTo ? `@${replyTo.user_name} ` + newComment : newComment}
                                onChange={(e) => setNewComment(replyTo ? e.target.value.replace(`@${replyTo.user_name} `, '') : e.target.value)}
                                placeholder={replyTo ? `Reply to ${replyTo.user_name}...` : "Add a comment..."}
                                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                                onKeyPress={(e) => {
                                  if (e.key === 'Enter') {
                                    addComment(cause.id, newComment, replyTo?.id);
                                  }
                                }}
                              />
                              <button
                                onClick={() => addComment(cause.id, newComment, replyTo?.id)}
                                className="px-3 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600 transition-colors"
                              >
                                Post
                              </button>
                            </div>
                            {replyTo && (
                              <button
                                onClick={() => setReplyTo(null)}
                                className="text-xs text-gray-500 mt-1 hover:text-gray-700"
                              >
                                Cancel reply
                              </button>
                            )}
                          </div>
                        )}

                        {/* Comments List */}
                        <div className="space-y-3 max-h-64 overflow-y-auto">
                          {comments[cause.id]?.comments?.map((commentGroup) => (
                            <div key={commentGroup.comment.id} className="space-y-2">
                              {/* Main Comment */}
                              <div className={`p-3 rounded-lg ${commentGroup.comment.is_admin_response ? 'bg-blue-50 border-l-4 border-blue-400' : 'bg-gray-50'}`}>
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="font-medium text-sm text-gray-800">
                                    {commentGroup.comment.user_name}
                                  </span>
                                  <span className={`px-2 py-1 rounded-full text-xs ${
                                    commentGroup.comment.user_type === 'business' ? 'bg-blue-100 text-blue-800' :
                                    commentGroup.comment.user_type === 'customer' ? 'bg-green-100 text-green-800' :
                                    'bg-purple-100 text-purple-800'
                                  }`}>
                                    {commentGroup.comment.user_type}
                                  </span>
                                  {commentGroup.comment.is_admin_response && (
                                    <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                                      ✅ Creator
                                    </span>
                                  )}
                                  <span className="text-xs text-gray-500">
                                    {new Date(commentGroup.comment.created_at).toLocaleDateString()}
                                  </span>
                                </div>
                                <p className="text-sm text-gray-700">{commentGroup.comment.comment}</p>
                                {currentUser && (
                                  <button
                                    onClick={() => setReplyTo(commentGroup.comment)}
                                    className="text-xs text-blue-600 hover:text-blue-800 mt-1"
                                  >
                                    Reply
                                  </button>
                                )}
                              </div>

                              {/* Replies */}
                              {commentGroup.replies?.map((reply) => (
                                <div key={reply.id} className={`ml-4 p-2 rounded-lg ${reply.is_admin_response ? 'bg-blue-50 border-l-4 border-blue-400' : 'bg-gray-100'}`}>
                                  <div className="flex items-center gap-2 mb-1">
                                    <span className="font-medium text-sm text-gray-800">
                                      {reply.user_name}
                                    </span>
                                    <span className={`px-2 py-1 rounded-full text-xs ${
                                      reply.user_type === 'business' ? 'bg-blue-100 text-blue-800' :
                                      reply.user_type === 'customer' ? 'bg-green-100 text-green-800' :
                                      'bg-purple-100 text-purple-800'
                                    }`}>
                                      {reply.user_type}
                                    </span>
                                    {reply.is_admin_response && (
                                      <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                                        ✅ Creator
                                      </span>
                                    )}
                                    <span className="text-xs text-gray-500">
                                      {new Date(reply.created_at).toLocaleDateString()}
                                    </span>
                                  </div>
                                  <p className="text-sm text-gray-700">{reply.comment}</p>
                                </div>
                              ))}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>

                  <button
                    onClick={() => setSelectedCause(cause)}
                    disabled={isExpired}
                    className={`w-full py-3 rounded-lg font-semibold transition-all ${
                      isExpired 
                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed' 
                        : 'bg-blue-500 text-white hover:bg-blue-600'
                    }`}
                  >
                    {isExpired ? 'Cause Expired' : 'Donate Now'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>

        {/* Enhanced Donation Modal */}
        {selectedCause && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 overflow-y-auto">
            <div className="bg-white rounded-xl p-8 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                Donate to {selectedCause.name}
              </h3>
              
              {/* Creator Info */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-blue-800">
                  <strong>Created by:</strong> 
                  {selectedCause.creator_website ? (
                    <a 
                      href={selectedCause.creator_website} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 ml-1"
                    >
                      {selectedCause.creator_name} 🔗
                    </a>
                  ) : (
                    <span className="ml-1">{selectedCause.creator_name}</span>
                  )}
                  <span className="text-blue-600 ml-2">({selectedCause.creator_type})</span>
                </p>
              </div>
              
              {/* User Type Selection */}
              {!currentUser && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                  <h4 className="font-semibold text-blue-800 mb-2">Donation Options</h4>
                  <div className="space-y-2">
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="donationType"
                        checked={!isAnonymous}
                        onChange={() => setIsAnonymous(false)}
                        className="mr-2"
                      />
                      <span>Donate with your details (for tracking)</span>
                    </label>
                    <label className="flex items-center">
                      <input
                        type="radio"
                        name="donationType"
                        checked={isAnonymous}
                        onChange={() => setIsAnonymous(true)}
                        className="mr-2"
                      />
                      <span>Anonymous donation</span>
                    </label>
                  </div>
                </div>
              )}

              {/* Anonymous Details */}
              {!currentUser && (
                <div className="grid md:grid-cols-2 gap-4 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
                    <input
                      type="text"
                      value={anonymousName}
                      onChange={(e) => setAnonymousName(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Your name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
                    <input
                      type="email"
                      value={anonymousEmail}
                      onChange={(e) => setAnonymousEmail(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="your@email.com"
                    />
                  </div>
                </div>
              )}
              
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Donation Amount ($)
                </label>
                <input
                  type="number"
                  min="1"
                  step="0.01"
                  value={donationAmount}
                  onChange={(e) => setDonationAmount(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0.00"
                />
                {donationAmount && (
                  <p className="text-sm text-green-600 mt-2">
                    Your ${donationAmount} will provide {(parseFloat(donationAmount) / selectedCause.cost_per_impact).toFixed(1)} {selectedCause.impact_metric}
                  </p>
                )}
              </div>

              {/* Payment Method Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">Payment Method</label>
                <div className="grid grid-cols-2 gap-3">
                  {selectedCause.payment_methods_accepted.map((method) => (
                    <button
                      key={method}
                      onClick={() => setPaymentMethod({ type: method, provider: method, details: {} })}
                      className={`p-3 rounded-lg border-2 transition-all ${
                        paymentMethod?.type === method
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      {method.replace(/_/g, " ").toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Message (Optional)
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  rows="3"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Share why this cause matters to you..."
                />
              </div>

              <div className="flex gap-4">
                <button
                  onClick={handleDonate}
                  disabled={!donationAmount || !paymentMethod || (!currentUser && (!anonymousName || !anonymousEmail))}
                  className="flex-1 bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  Donate ${donationAmount || "0"} Now
                </button>
                <button
                  onClick={() => setSelectedCause(null)}
                  className="flex-1 bg-gray-300 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-400 transition-all"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

// Enhanced Leaderboard Section with Cause Reports
const LeaderboardSection = () => {
  const [businessLeaderboard, setBusinessLeaderboard] = useState([]);
  const [customerLeaderboard, setCustomerLeaderboard] = useState([]);
  const [causeLeaderboard, setCauseLeaderboard] = useState([]);
  const [activeTab, setActiveTab] = useState("businesses");

  useEffect(() => {
    fetchLeaderboards();
  }, []);

  const fetchLeaderboards = async () => {
    try {
      const [businessRes, customerRes, causeRes] = await Promise.all([
        axios.get(`${API}/leaderboards/businesses`),
        axios.get(`${API}/leaderboards/customers`),
        axios.get(`${API}/leaderboards/causes`)
      ]);
      setBusinessLeaderboard(businessRes.data.leaderboard);
      setCustomerLeaderboard(customerRes.data.leaderboard);
      setCauseLeaderboard(causeRes.data.leaderboard);
    } catch (error) {
      console.error("Error fetching leaderboards:", error);
    }
  };

  const getRankColor = (rank) => {
    switch (rank) {
      case 1: return "text-yellow-600 bg-yellow-100";
      case 2: return "text-gray-600 bg-gray-100";
      case 3: return "text-amber-600 bg-amber-100";
      default: return "text-blue-600 bg-blue-100";
    }
  };

  const getRankIcon = (rank) => {
    switch (rank) {
      case 1: return "🥇";
      case 2: return "🥈";
      case 3: return "🥉";
      default: return "🏅";
    }
  };

  return (
    <div className="py-20 px-4 bg-gradient-to-br from-gray-50 to-white">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Impact Champions
          </h2>
          <p className="text-xl text-gray-600">
            Celebrating those making the biggest difference with detailed contribution reports
          </p>
        </div>

        <div className="flex justify-center mb-8">
          <div className="bg-white rounded-lg p-1 shadow-lg">
            <button
              onClick={() => setActiveTab("businesses")}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === "businesses"
                  ? "bg-blue-500 text-white shadow-md"
                  : "text-gray-600 hover:text-blue-500"
              }`}
            >
              Top Businesses
            </button>
            <button
              onClick={() => setActiveTab("customers")}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === "customers"
                  ? "bg-blue-500 text-white shadow-md"
                  : "text-gray-600 hover:text-blue-500"
              }`}
            >
              Top Contributors
            </button>
            <button
              onClick={() => setActiveTab("causes")}
              className={`px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === "causes"
                  ? "bg-blue-500 text-white shadow-md"
                  : "text-gray-600 hover:text-blue-500"
              }`}
            >
              Top Causes
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-1 gap-8">
          {/* Business Leaderboard */}
          {activeTab === "businesses" && (
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">
                Businesses by Total Impact
              </h3>
              <div className="space-y-4">
                {businessLeaderboard.map((entry) => (
                  <div key={entry.business.id} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold ${getRankColor(entry.rank)}`}>
                          {getRankIcon(entry.rank)}
                        </div>
                        <div>
                          <h4 className="font-semibold text-lg text-gray-800">{entry.business.name}</h4>
                          <p className="text-gray-600">{entry.business.industry}</p>
                          {entry.business.website && (
                            <a href={entry.business.website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 text-sm">
                              Visit Website 🔗
                            </a>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-green-600">
                          ${entry.metric_value.toFixed(0)}
                        </div>
                        <div className="text-sm text-gray-500">Total Impact</div>
                        <div className="text-sm text-gray-500">Account: {entry.business.account_number}</div>
                      </div>
                    </div>

                    {/* Causes Supported */}
                    {entry.causes_supported && entry.causes_supported.length > 0 && (
                      <div className="mt-4">
                        <h5 className="font-medium text-gray-700 mb-2">Causes Supported:</h5>
                        <div className="flex flex-wrap gap-2">
                          {entry.causes_supported.map((cause, index) => (
                            <span key={index} className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                              {cause.name} ({cause.category})
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Settlement Info */}
                    {entry.settlement_info && (
                      <div className="mt-4 bg-gray-50 rounded-lg p-3">
                        <h5 className="font-medium text-gray-700 mb-2">Settlement Information:</h5>
                        <div className="text-sm text-gray-600">
                          {entry.settlement_info.account_number && (
                            <p>Account: {entry.settlement_info.account_number}</p>
                          )}
                          {entry.settlement_info.phone_number && (
                            <p>Phone: {entry.settlement_info.phone_number}</p>
                          )}
                          {entry.settlement_info.bank_name && (
                            <p>Bank: {entry.settlement_info.bank_name}</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Customer Leaderboard */}
          {activeTab === "customers" && (
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">
                Top Contributors with Cause Breakdown
              </h3>
              <div className="space-y-4">
                {customerLeaderboard.map((entry) => (
                  <div key={entry.customer.id} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold ${getRankColor(entry.rank)}`}>
                          {getRankIcon(entry.rank)}
                        </div>
                        <div>
                          <h4 className="font-semibold text-lg text-gray-800">{entry.customer.name}</h4>
                          <p className="text-gray-600">{entry.customer.contribution_count} contributions</p>
                          <p className="text-sm text-gray-500">Account: {entry.customer.account_number}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-green-600">
                          ${entry.metric_value.toFixed(0)}
                        </div>
                        <div className="text-sm text-gray-500">Total Donated</div>
                      </div>
                    </div>

                    {/* Cause Breakdown */}
                    {entry.cause_breakdown && entry.cause_breakdown.length > 0 && (
                      <div className="mt-4">
                        <h5 className="font-medium text-gray-700 mb-3">Contribution Breakdown by Cause:</h5>
                        <div className="space-y-2">
                          {entry.cause_breakdown.map((cause, index) => (
                            <div key={index} className="flex justify-between items-center bg-gray-50 rounded-lg p-3">
                              <div>
                                <span className="font-medium text-gray-800">{cause.cause_name}</span>
                                <span className="text-gray-600 text-sm ml-2">({cause.category})</span>
                              </div>
                              <div className="text-right">
                                <div className="font-bold text-green-600">${cause.total_contributed.toFixed(0)}</div>
                                <div className="text-sm text-gray-500">{cause.contribution_count} donations</div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Settlement Info */}
                    {entry.settlement_info && (
                      <div className="mt-4 bg-gray-50 rounded-lg p-3">
                        <h5 className="font-medium text-gray-700 mb-2">Settlement Information:</h5>
                        <div className="text-sm text-gray-600">
                          {entry.settlement_info.phone_number && (
                            <p>Phone: {entry.settlement_info.phone_number}</p>
                          )}
                          {entry.settlement_info.account_type && (
                            <p>Type: {entry.settlement_info.account_type}</p>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Cause Leaderboard */}
          {activeTab === "causes" && (
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">
                Top Performing Causes with Contribution Reports
              </h3>
              <div className="space-y-4">
                {causeLeaderboard.map((entry) => (
                  <div key={entry.cause.id} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold ${getRankColor(entry.rank)}`}>
                          {getRankIcon(entry.rank)}
                        </div>
                        <div>
                          <h4 className="font-semibold text-lg text-gray-800">{entry.cause.name}</h4>
                          <p className="text-gray-600">{entry.cause.category}</p>
                          <p className="text-sm text-gray-600">
                            Created by: 
                            {entry.cause.creator_website ? (
                              <a href={entry.cause.creator_website} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:text-blue-800 ml-1">
                                {entry.cause.creator_name} 🔗
                              </a>
                            ) : (
                              <span className="ml-1">{entry.cause.creator_name}</span>
                            )}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-green-600">
                          ${entry.metric_value.toFixed(0)}
                        </div>
                        <div className="text-sm text-gray-500">Total Raised</div>
                        {entry.progress_percentage && (
                          <div className="text-sm text-gray-500">{entry.progress_percentage.toFixed(1)}% of goal</div>
                        )}
                      </div>
                    </div>

                    {/* Progress Bar */}
                    {entry.cause.goal_amount && (
                      <div className="mb-4">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full transition-all" 
                            style={{ width: `${Math.min(entry.progress_percentage, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    )}

                    {/* Contributor Statistics */}
                    <div className="grid md:grid-cols-3 gap-4 mt-4">
                      <div className="bg-blue-50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-blue-600">{entry.contributor_stats.total_contributors}</div>
                        <div className="text-sm text-blue-800">Registered Contributors</div>
                      </div>
                      <div className="bg-green-50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-green-600">{entry.contributor_stats.anonymous_contributions}</div>
                        <div className="text-sm text-green-800">Anonymous Donations</div>
                      </div>
                      <div className="bg-purple-50 rounded-lg p-3 text-center">
                        <div className="text-2xl font-bold text-purple-600">{entry.contributor_stats.recent_contributions}</div>
                        <div className="text-sm text-purple-800">Recent (7 days)</div>
                      </div>
                    </div>

                    {/* Impact Information */}
                    <div className="mt-4 bg-gray-50 rounded-lg p-3">
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-600">
                            <strong>Impact Generated:</strong> {entry.cause.total_impact_units.toFixed(0)} {entry.cause.impact_metric}
                          </p>
                          <p className="text-sm text-gray-600">
                            <strong>Cost per Impact:</strong> ${entry.cause.cost_per_impact}
                          </p>
                        </div>
                        <div>
                          {entry.cause.end_date && (
                            <p className="text-sm text-gray-600">
                              <strong>Ends:</strong> {new Date(entry.cause.end_date).toLocaleDateString()}
                            </p>
                          )}
                          {entry.cause.expired && (
                            <span className="inline-block px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">
                              ❌ Expired
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Subscription Management Component
const SubscriptionManager = ({ userId, userType }) => {
  const [currentSubscription, setCurrentSubscription] = useState(null);
  const [plans, setPlans] = useState(null);
  const [selectedPlan, setSelectedPlan] = useState(null);

  useEffect(() => {
    fetchSubscription();
    fetchPlans();
  }, [userId]);

  const fetchSubscription = async () => {
    try {
      const response = await axios.get(`${API}/subscriptions/${userId}?user_type=${userType}`);
      setCurrentSubscription(response.data);
    } catch (error) {
      console.error("Error fetching subscription:", error);
    }
  };

  const fetchPlans = async () => {
    try {
      const response = await axios.get(`${API}/subscription-plans`);
      setPlans(response.data);
    } catch (error) {
      console.error("Error fetching plans:", error);
    }
  };

  const subscribeToPlan = async (planType) => {
    try {
      await axios.post(`${API}/subscriptions?user_id=${userId}&user_type=${userType}`, {
        plan_type: planType,
        auto_renew: true
      });
      alert("Subscription created successfully!");
      fetchSubscription();
    } catch (error) {
      console.error("Error creating subscription:", error);
      alert("Error creating subscription: " + (error.response?.data?.detail || error.message));
    }
  };

  if (!plans) return <div>Loading subscription plans...</div>;

  const userPlans = userType === "customer" ? plans.individual : plans.business;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
          Subscription Management
        </h2>

        {/* Current Subscription */}
        {currentSubscription && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
            <h3 className="text-xl font-semibold text-green-800 mb-2">Current Subscription</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <p><strong>Plan:</strong> {currentSubscription.plan_type}</p>
                <p><strong>Status:</strong> {currentSubscription.status}</p>
                <p><strong>Amount:</strong> ${currentSubscription.amount}</p>
              </div>
              <div>
                <p><strong>Started:</strong> {new Date(currentSubscription.start_date).toLocaleDateString()}</p>
                <p><strong>Ends:</strong> {new Date(currentSubscription.end_date).toLocaleDateString()}</p>
                <p><strong>Auto-renew:</strong> {currentSubscription.auto_renew ? "Yes" : "No"}</p>
              </div>
            </div>
          </div>
        )}

        {/* Available Plans */}
        <div className="grid md:grid-cols-3 gap-6">
          {Object.entries(userPlans).map(([planType, planDetails]) => (
            <div key={planType} className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 transition-all">
              <div className="text-center mb-4">
                <h3 className="text-xl font-semibold text-gray-800 capitalize">{planType}</h3>
                <div className="text-3xl font-bold text-blue-600 my-2">${planDetails.price}</div>
                <p className="text-gray-600">per {planType === "monthly" ? "month" : "year"}</p>
              </div>
              
              <div className="space-y-2 mb-6">
                {planDetails.features.map((feature, index) => (
                  <div key={index} className="flex items-center">
                    <span className="text-green-500 mr-2">✓</span>
                    <span className="text-sm text-gray-600">{feature.replace(/_/g, " ")}</span>
                  </div>
                ))}
              </div>
              
              <button
                onClick={() => subscribeToPlan(planType)}
                disabled={currentSubscription?.plan_type === planType}
                className={`w-full py-2 rounded-lg font-semibold transition-all ${
                  currentSubscription?.plan_type === planType
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-blue-500 text-white hover:bg-blue-600"
                }`}
              >
                {currentSubscription?.plan_type === planType ? "Current Plan" : "Subscribe"}
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Settlement Information Component
const SettlementManager = ({ userId, userType }) => {
  const [settlementInfo, setSettlementInfo] = useState({
    account_number: "",
    phone_number: "",
    bank_name: "",
    bank_code: "",
    account_type: "savings"
  });

  const handleSave = async () => {
    try {
      const endpoint = userType === "customer" 
        ? `${API}/customers/${userId}/settlement`
        : `${API}/businesses/${userId}/settlement`;
      
      await axios.put(endpoint, settlementInfo);
      alert("Settlement information saved successfully!");
    } catch (error) {
      console.error("Error saving settlement info:", error);
      alert("Error saving settlement information");
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">
          Settlement Information
        </h2>
        <p className="text-gray-600 mb-8 text-center">
          Update your payment details for receiving funds
        </p>

        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Account Number</label>
              <input
                type="text"
                value={settlementInfo.account_number}
                onChange={(e) => setSettlementInfo({...settlementInfo, account_number: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Bank account number"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
              <input
                type="tel"
                value={settlementInfo.phone_number}
                onChange={(e) => setSettlementInfo({...settlementInfo, phone_number: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="+1234567890"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Bank Name</label>
              <input
                type="text"
                value={settlementInfo.bank_name}
                onChange={(e) => setSettlementInfo({...settlementInfo, bank_name: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Your bank name"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Account Type</label>
              <select
                value={settlementInfo.account_type}
                onChange={(e) => setSettlementInfo({...settlementInfo, account_type: e.target.value})}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="savings">Savings</option>
                <option value="checking">Checking</option>
                <option value="momo">Mobile Money</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleSave}
            className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition-all"
          >
            Save Settlement Information
          </button>
        </div>
      </div>
    </div>
  );
};

// Hero Section Component
const HeroSection = () => {
  return (
    <div className="relative bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 text-white py-20 px-4">
      <div className="absolute inset-0 bg-black opacity-20"></div>
      <div className="relative max-w-6xl mx-auto text-center">
        <div className="mb-8">
          <img 
            src="https://images.unsplash.com/photo-1469571486292-0ba58a3f068b" 
            alt="Social Impact" 
            className="mx-auto w-32 h-32 rounded-full object-cover shadow-xl border-4 border-white"
          />
        </div>
        <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
          Turn Every Sale Into 
          <span className="text-yellow-300"> Social Impact</span>
        </h1>
        <p className="text-xl md:text-2xl mb-8 opacity-90 max-w-3xl mx-auto">
          ImpactLink connects businesses/individuals who are supporting social change with people who want to support social change through donation and volunteering. 
          Donate directly and track your impact in real-time.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <button className="bg-yellow-400 text-black px-8 py-4 rounded-full font-semibold text-lg hover:bg-yellow-300 transform hover:scale-105 transition-all shadow-lg">
            Start Making Impact
          </button>
          <button className="border-2 border-white text-white px-8 py-4 rounded-full font-semibold text-lg hover:bg-white hover:text-purple-600 transition-all">
            Browse Causes
          </button>
        </div>
      </div>
    </div>
  );
};

// Features Section Component (Enhanced)
const FeaturesSection = () => {
  const features = [
    {
      title: "Cause Expiration & Tracking",
      description: "Causes have start and end dates with automatic expiration handling and progress tracking",
      icon: "⏰",
      color: "bg-orange-100 border-orange-200"
    },
    {
      title: "Creator Attribution",
      description: "See who created each cause with direct links to their websites and profiles",
      icon: "👥",
      color: "bg-blue-100 border-blue-200"
    },
    {
      title: "Advanced Filtering",
      description: "Filter causes by category, status, expiration, and sort by various metrics",
      icon: "🔍",
      color: "bg-green-100 border-green-200"
    },
    {
      title: "Subscription Plans",
      description: "Monthly and yearly subscription options for enhanced features and capabilities",
      icon: "⭐",
      color: "bg-yellow-100 border-yellow-200"
    },
    {
      title: "Settlement System",
      description: "Account numbers and phone numbers for secure fund settlement and withdrawals",
      icon: "💰",
      color: "bg-purple-100 border-purple-200"
    },
    {
      title: "Demo Platform",
      description: "Complete demo users for testing business, customer, and admin functionalities",
      icon: "🎮",
      color: "bg-red-100 border-red-200"
    }
  ];

  return (
    <div className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Complete Impact Management Platform
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Advanced features for cause management, user attribution, subscriptions, and comprehensive tracking
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <div key={index} className={`${feature.color} border-2 rounded-xl p-6 text-center hover:shadow-lg transition-all`}>
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Placeholder components for brevity
const CustomerRegistration = ({ onCustomerCreate }) => <div></div>;
const BusinessSetup = ({ onBusinessCreate }) => <div></div>;
const BusinessDashboard = ({ business }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [causes, setCauses] = useState([]);
  const [comments, setComments] = useState({});
  const [selectedTab, setSelectedTab] = useState("overview");
  const [loading, setLoading] = useState(true);
  const [replyText, setReplyText] = useState("");
  const [replyingTo, setReplyingTo] = useState(null);
  const { currentUser, userType } = useUser();

  useEffect(() => {
    if (business) {
      fetchDashboardData();
      fetchBusinessCauses();
    }
  }, [business]);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/impact/dashboard/${business.id}`);
      setDashboardData(response.data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchBusinessCauses = async () => {
    try {
      const response = await axios.get(`${API}/causes?creator_type=business&creator_id=${business.id}&active_only=false`);
      setCauses(response.data);
      
      // Fetch comments for each cause
      for (const cause of response.data) {
        fetchCauseComments(cause.id);
      }
    } catch (error) {
      console.error("Error fetching business causes:", error);
    }
  };

  const fetchCauseComments = async (causeId) => {
    try {
      const response = await axios.get(`${API}/causes/${causeId}/comments`);
      setComments(prev => ({
        ...prev,
        [causeId]: response.data
      }));
    } catch (error) {
      console.error("Error fetching cause comments:", error);
    }
  };

  const replyToComment = async (causeId, parentCommentId, replyText) => {
    if (!replyText.trim()) return;

    try {
      await axios.post(`${API}/causes/${causeId}/comments?user_id=${business.id}&user_type=business`, {
        comment: replyText,
        parent_comment_id: parentCommentId
      });
      
      setReplyText("");
      setReplyingTo(null);
      fetchCauseComments(causeId);
    } catch (error) {
      console.error("Error replying to comment:", error);
    }
  };

  const getCauseHealth = (cause) => {
    const progressPercentage = cause.goal_amount ? (cause.total_raised / cause.goal_amount) * 100 : 0;
    const daysRemaining = cause.end_date ? Math.ceil((new Date(cause.end_date) - new Date()) / (1000 * 60 * 60 * 24)) : null;
    const isExpired = cause.expired || (daysRemaining !== null && daysRemaining <= 0);
    
    if (isExpired) return { status: "expired", color: "red", text: "Expired" };
    if (progressPercentage >= 100) return { status: "completed", color: "green", text: "Goal Reached" };
    if (progressPercentage >= 75) return { status: "excellent", color: "green", text: "Excellent" };
    if (progressPercentage >= 50) return { status: "good", color: "yellow", text: "Good" };
    if (progressPercentage >= 25) return { status: "fair", color: "orange", text: "Fair" };
    return { status: "poor", color: "red", text: "Needs Attention" };
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="flex justify-center items-center h-64">
          <div className="text-lg text-gray-600">Loading dashboard...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold text-gray-800">Business Dashboard</h1>
          <p className="text-gray-600 mt-2">Welcome back, {business.name}</p>
        </div>

        <div className="p-6">
          <div className="mb-6">
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setSelectedTab("overview")}
                className={`px-4 py-2 font-medium ${selectedTab === "overview" ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-600"}`}
              >
                Overview
              </button>
              <button
                onClick={() => setSelectedTab("causes")}
                className={`px-4 py-2 font-medium ${selectedTab === "causes" ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-600"}`}
              >
                My Causes
              </button>
              <button
                onClick={() => setSelectedTab("comments")}
                className={`px-4 py-2 font-medium ${selectedTab === "comments" ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-600"}`}
              >
                Comments & Responses
              </button>
            </div>
          </div>

          {selectedTab === "overview" && dashboardData && (
            <div className="space-y-6">
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-800">Total Sales</h3>
                  <p className="text-2xl font-bold text-blue-600">${dashboardData.total_sales?.toFixed(2) || '0.00'}</p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-green-800">Total Impact</h3>
                  <p className="text-2xl font-bold text-green-600">${dashboardData.total_impact?.toFixed(2) || '0.00'}</p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-purple-800">My Causes</h3>
                  <p className="text-2xl font-bold text-purple-600">{causes.length}</p>
                </div>
                <div className="bg-orange-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-orange-800">Impact Rate</h3>
                  <p className="text-2xl font-bold text-orange-600">
                    {dashboardData.impact_percentage?.toFixed(1) || '0'}%
                  </p>
                </div>
              </div>

              {/* Cause Breakdown */}
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Impact Allocation Breakdown</h3>
                {dashboardData.cause_breakdown && Object.keys(dashboardData.cause_breakdown).length > 0 ? (
                  <div className="space-y-3">
                    {Object.entries(dashboardData.cause_breakdown).map(([causeId, causeData]) => (
                      <div key={causeId} className="flex justify-between items-center bg-gray-50 rounded-lg p-3">
                        <div>
                          <span className="font-medium text-gray-800">{causeData.name}</span>
                          <span className="text-gray-600 text-sm ml-2">({causeData.category})</span>
                          {causeData.expired && <span className="text-red-600 text-sm ml-2">[Expired]</span>}
                        </div>
                        <div className="text-right">
                          <div className="font-bold text-blue-600">{causeData.percentage}%</div>
                          <div className="text-sm text-gray-500">${causeData.total_contribution?.toFixed(2) || '0.00'}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500">No impact allocation set up yet.</p>
                )}
              </div>
            </div>
          )}

          {selectedTab === "causes" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 gap-6">
                {causes.length > 0 ? causes.map((cause) => {
                  const health = getCauseHealth(cause);
                  const progressPercentage = cause.goal_amount ? (cause.total_raised / cause.goal_amount) * 100 : 0;
                  const daysRemaining = cause.end_date ? Math.ceil((new Date(cause.end_date) - new Date()) / (1000 * 60 * 60 * 24)) : null;
                  
                  return (
                    <div key={cause.id} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-bold text-gray-800">{cause.name}</h3>
                        <span className={`px-3 py-1 rounded-full text-white text-sm font-medium bg-${health.color}-500`}>
                          {health.text}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                        <div>
                          <p className="text-sm text-gray-600">Total Raised</p>
                          <p className="text-lg font-bold text-green-600">${cause.total_raised.toFixed(2)}</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Goal Progress</p>
                          <p className="text-lg font-bold text-blue-600">{progressPercentage.toFixed(1)}%</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-600">Days Remaining</p>
                          <p className={`text-lg font-bold ${daysRemaining && daysRemaining > 0 ? 'text-orange-600' : 'text-red-600'}`}>
                            {daysRemaining && daysRemaining > 0 ? `${daysRemaining} days` : 'Ended'}
                          </p>
                        </div>
                      </div>

                      {/* Progress Bar */}
                      <div className="mb-4">
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-green-500 h-2 rounded-full transition-all" 
                            style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                          ></div>
                        </div>
                      </div>

                      {/* Comments Summary */}
                      <div className="bg-gray-50 rounded-lg p-3">
                        <p className="text-sm text-gray-600">
                          <strong>Comments:</strong> {comments[cause.id]?.total_comments || 0} total
                        </p>
                        {comments[cause.id] && comments[cause.id].comments?.length > 0 && (
                          <p className="text-sm text-gray-600">
                            Latest: "{comments[cause.id].comments[comments[cause.id].comments.length - 1]?.comment?.comment?.substring(0, 50)}..."
                          </p>
                        )}
                      </div>
                    </div>
                  );
                }) : (
                  <div className="text-center py-8">
                    <p className="text-gray-500 mb-4">You haven't created any causes yet.</p>
                    <button
                      onClick={() => window.location.hash = 'create-cause'}
                      className="bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600"
                    >
                      Create Your First Cause
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}

          {selectedTab === "comments" && (
            <div className="space-y-6">
              {causes.map((cause) => {
                const causeComments = comments[cause.id];
                if (!causeComments || causeComments.total_comments === 0) return null;

                return (
                  <div key={cause.id} className="border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-bold text-gray-800 mb-4">{cause.name}</h3>
                    
                    <div className="space-y-4">
                      {causeComments.comments?.map((commentGroup) => (
                        <div key={commentGroup.comment.id} className="space-y-2">
                          {/* Main Comment */}
                          <div className="bg-gray-50 rounded-lg p-3">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="font-medium text-gray-800">{commentGroup.comment.user_name}</span>
                              <span className={`px-2 py-1 rounded-full text-xs ${
                                commentGroup.comment.user_type === 'business' ? 'bg-blue-100 text-blue-800' :
                                commentGroup.comment.user_type === 'customer' ? 'bg-green-100 text-green-800' :
                                'bg-purple-100 text-purple-800'
                              }`}>
                                {commentGroup.comment.user_type}
                              </span>
                              <span className="text-xs text-gray-500">
                                {new Date(commentGroup.comment.created_at).toLocaleDateString()}
                              </span>
                            </div>
                            <p className="text-gray-700 mb-2">{commentGroup.comment.comment}</p>
                            
                            {/* Reply Button */}
                            <button
                              onClick={() => setReplyingTo(replyingTo === commentGroup.comment.id ? null : commentGroup.comment.id)}
                              className="text-blue-600 hover:text-blue-800 text-sm"
                            >
                              {replyingTo === commentGroup.comment.id ? 'Cancel Reply' : 'Reply'}
                            </button>

                            {/* Reply Form */}
                            {replyingTo === commentGroup.comment.id && (
                              <div className="mt-3 flex gap-2">
                                <input
                                  type="text"
                                  value={replyText}
                                  onChange={(e) => setReplyText(e.target.value)}
                                  placeholder="Write your reply..."
                                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:border-blue-500"
                                  onKeyPress={(e) => {
                                    if (e.key === 'Enter') {
                                      replyToComment(cause.id, commentGroup.comment.id, replyText);
                                    }
                                  }}
                                />
                                <button
                                  onClick={() => replyToComment(cause.id, commentGroup.comment.id, replyText)}
                                  className="px-3 py-2 bg-blue-500 text-white rounded-lg text-sm hover:bg-blue-600"
                                >
                                  Reply
                                </button>
                              </div>
                            )}
                          </div>

                          {/* Replies */}
                          {commentGroup.replies?.map((reply) => (
                            <div key={reply.id} className={`ml-6 p-2 rounded-lg ${reply.is_admin_response ? 'bg-blue-50 border-l-4 border-blue-400' : 'bg-gray-100'}`}>
                              <div className="flex items-center gap-2 mb-1">
                                <span className="font-medium text-sm text-gray-800">{reply.user_name}</span>
                                <span className={`px-2 py-1 rounded-full text-xs ${
                                  reply.user_type === 'business' ? 'bg-blue-100 text-blue-800' :
                                  reply.user_type === 'customer' ? 'bg-green-100 text-green-800' :
                                  'bg-purple-100 text-purple-800'
                                }`}>
                                  {reply.user_type}
                                </span>
                                {reply.is_admin_response && (
                                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                                    ✅ You
                                  </span>
                                )}
                                <span className="text-xs text-gray-500">
                                  {new Date(reply.created_at).toLocaleDateString()}
                                </span>
                              </div>
                              <p className="text-sm text-gray-700">{reply.comment}</p>
                            </div>
                          ))}
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}

              {causes.every(cause => !comments[cause.id] || comments[cause.id].total_comments === 0) && (
                <div className="text-center py-8">
                  <p className="text-gray-500">No comments on your causes yet.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// User Cause Creation Component
const CreateCauseForm = () => {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    category: "Education",
    impact_metric: "",
    cost_per_impact: "",
    goal_amount: "",
    end_date: "",
    image_url: "",
    payment_methods_accepted: ["card", "momo", "bank_transfer"],
    volunteer_opportunities: [],
    settlement_info: {
      account_number: "",
      phone_number: "",
      bank_name: "",
      account_type: "checking"
    }
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const { currentUser, userType } = useUser();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    if (name.startsWith('settlement_')) {
      const field = name.replace('settlement_', '');
      setFormData(prev => ({
        ...prev,
        settlement_info: {
          ...prev.settlement_info,
          [field]: value
        }
      }));
    } else {
      setFormData(prev => ({ ...prev, [name]: value }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await axios.post(`${API}/users/${currentUser.id}/causes?user_type=${userType}`, {
        ...formData,
        cost_per_impact: parseFloat(formData.cost_per_impact),
        goal_amount: parseFloat(formData.goal_amount),
        end_date: new Date(formData.end_date).toISOString(),
        volunteer_opportunities: formData.volunteer_opportunities.filter(v => v.trim())
      });

      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        setFormData({
          name: "",
          description: "",
          category: "Education",
          impact_metric: "",
          cost_per_impact: "",
          goal_amount: "",
          end_date: "",
          image_url: "",
          payment_methods_accepted: ["card", "momo", "bank_transfer"],
          volunteer_opportunities: [],
          settlement_info: {
            account_number: "",
            phone_number: "",
            bank_name: "",
            account_type: "checking"
          }
        });
      }, 3000);
    } catch (error) {
      console.error("Error creating cause:", error);
      alert("Failed to create cause. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const addVolunteerOpportunity = () => {
    setFormData(prev => ({
      ...prev,
      volunteer_opportunities: [...prev.volunteer_opportunities, ""]
    }));
  };

  const updateVolunteerOpportunity = (index, value) => {
    setFormData(prev => ({
      ...prev,
      volunteer_opportunities: prev.volunteer_opportunities.map((item, i) => 
        i === index ? value : item
      )
    }));
  };

  const removeVolunteerOpportunity = (index) => {
    setFormData(prev => ({
      ...prev,
      volunteer_opportunities: prev.volunteer_opportunities.filter((_, i) => i !== index)
    }));
  };

  if (success) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
          <div className="text-green-600 text-6xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-green-800 mb-2">Cause Created Successfully!</h2>
          <p className="text-green-700">Your cause has been created and is now live on the platform.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6">Create Your Cause</h2>
        <p className="text-gray-600 mb-8">Share your mission and start making an impact</p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Cause Name *</label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                placeholder="e.g., Community Education Initiative"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Category *</label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              >
                <option value="Education">Education</option>
                <option value="Health">Health</option>
                <option value="Environment">Environment</option>
                <option value="Poverty">Poverty</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleInputChange}
              required
              rows="4"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="Describe your cause and its impact..."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Impact Metric *</label>
              <input
                type="text"
                name="impact_metric"
                value={formData.impact_metric}
                onChange={handleInputChange}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                placeholder="e.g., children educated"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Cost Per Impact ($) *</label>
              <input
                type="number"
                name="cost_per_impact"
                value={formData.cost_per_impact}
                onChange={handleInputChange}
                required
                step="0.01"
                min="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                placeholder="25.00"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Goal Amount ($) *</label>
              <input
                type="number"
                name="goal_amount"
                value={formData.goal_amount}
                onChange={handleInputChange}
                required
                step="0.01"
                min="0"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                placeholder="10000.00"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">End Date *</label>
              <input
                type="date"
                name="end_date"
                value={formData.end_date}
                onChange={handleInputChange}
                required
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Image URL (optional)</label>
              <input
                type="url"
                name="image_url"
                value={formData.image_url}
                onChange={handleInputChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                placeholder="https://example.com/image.jpg"
              />
            </div>
          </div>

          {/* Settlement Information */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Settlement Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Account Number *</label>
                <input
                  type="text"
                  name="settlement_account_number"
                  value={formData.settlement_info.account_number}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  placeholder="Bank account number"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Phone Number</label>
                <input
                  type="tel"
                  name="settlement_phone_number"
                  value={formData.settlement_info.phone_number}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  placeholder="+1-234-567-8900"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Bank Name *</label>
                <input
                  type="text"
                  name="settlement_bank_name"
                  value={formData.settlement_info.bank_name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                  placeholder="Bank name"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Account Type</label>
                <select
                  name="settlement_account_type"
                  value={formData.settlement_info.account_type}
                  onChange={handleInputChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                >
                  <option value="checking">Checking</option>
                  <option value="savings">Savings</option>
                  <option value="momo">Mobile Money</option>
                </select>
              </div>
            </div>
          </div>

          {/* Volunteer Opportunities */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Volunteer Opportunities</h3>
            <div className="space-y-3">
              {formData.volunteer_opportunities.map((opportunity, index) => (
                <div key={index} className="flex gap-2">
                  <input
                    type="text"
                    value={opportunity}
                    onChange={(e) => updateVolunteerOpportunity(index, e.target.value)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
                    placeholder="e.g., tutoring, event organization"
                  />
                  <button
                    type="button"
                    onClick={() => removeVolunteerOpportunity(index)}
                    className="px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button
                type="button"
                onClick={addVolunteerOpportunity}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
              >
                Add Volunteer Opportunity
              </button>
            </div>
          </div>

          <div className="flex justify-end pt-6">
            <button
              type="submit"
              disabled={loading}
              className={`px-8 py-3 rounded-lg font-semibold text-white transition-all ${
                loading 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-blue-500 hover:bg-blue-600'
              }`}
            >
              {loading ? 'Creating Cause...' : 'Create Cause'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
const AdminDashboard = () => {
  const [settlements, setSettlements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState("settlements");

  useEffect(() => {
    fetchSettlements();
  }, []);

  const fetchSettlements = async () => {
    try {
      const response = await axios.get(`${API}/admin/settlements`);
      setSettlements(response.data.settlements);
    } catch (error) {
      console.error("Error fetching settlements:", error);
    } finally {
      setLoading(false);
    }
  };

  const initiatePayment = async (causeId) => {
    try {
      const response = await axios.post(`${API}/admin/settlements/${causeId}/initiate-payment`, {
        admin_id: "admin",
        payment_method: {
          type: "bank_transfer",
          provider: "bank"
        }
      });
      
      alert(`Payment initiated successfully! Reference: ${response.data.payment_reference}`);
      fetchSettlements(); // Refresh data
    } catch (error) {
      console.error("Error initiating payment:", error);
      alert("Failed to initiate payment. Please try again.");
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="flex justify-center items-center h-64">
          <div className="text-lg text-gray-600">Loading settlement data...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold text-gray-800">Admin Settlement Center</h1>
          <p className="text-gray-600 mt-2">Manage cause settlements and payments</p>
        </div>

        <div className="p-6">
          <div className="mb-6">
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setSelectedTab("settlements")}
                className={`px-4 py-2 font-medium ${selectedTab === "settlements" ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-600"}`}
              >
                Settlement Overview
              </button>
              <button
                onClick={() => setSelectedTab("analytics")}
                className={`px-4 py-2 font-medium ${selectedTab === "analytics" ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-600"}`}
              >
                Payment Analytics
              </button>
            </div>
          </div>

          {selectedTab === "settlements" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-800">Total Pending</h3>
                  <p className="text-2xl font-bold text-blue-600">
                    ${settlements.reduce((sum, s) => sum + s.settlement.pending_amount, 0).toFixed(2)}
                  </p>
                </div>
                <div className="bg-green-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-green-800">Total Settled</h3>
                  <p className="text-2xl font-bold text-green-600">
                    ${settlements.reduce((sum, s) => sum + s.settlement.total_settled, 0).toFixed(2)}
                  </p>
                </div>
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h3 className="text-lg font-semibold text-purple-800">Active Causes</h3>
                  <p className="text-2xl font-bold text-purple-600">
                    {settlements.filter(s => s.settlement.pending_amount > 0).length}
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full border-collapse border border-gray-200">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="border border-gray-200 px-4 py-3 text-left">Cause</th>
                      <th className="border border-gray-200 px-4 py-3 text-left">Creator</th>
                      <th className="border border-gray-200 px-4 py-3 text-right">Direct Donations</th>
                      <th className="border border-gray-200 px-4 py-3 text-right">Business Donations</th>
                      <th className="border border-gray-200 px-4 py-3 text-right">Total Donations</th>
                      <th className="border border-gray-200 px-4 py-3 text-right">Pending Payment</th>
                      <th className="border border-gray-200 px-4 py-3 text-center">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {settlements.map((settlement) => (
                      <tr key={settlement.cause.id} className="hover:bg-gray-50">
                        <td className="border border-gray-200 px-4 py-3">
                          <div>
                            <div className="font-medium text-gray-800">{settlement.cause.name}</div>
                            <div className="text-sm text-gray-500">{settlement.cause.category}</div>
                          </div>
                        </td>
                        <td className="border border-gray-200 px-4 py-3">
                          <div>
                            <div className="font-medium text-gray-800">{settlement.cause.creator_name}</div>
                            <div className="text-sm text-gray-500">{settlement.cause.creator_type}</div>
                          </div>
                        </td>
                        <td className="border border-gray-200 px-4 py-3 text-right">
                          <span className="font-medium text-green-600">
                            ${settlement.direct_donations.toFixed(2)}
                          </span>
                        </td>
                        <td className="border border-gray-200 px-4 py-3 text-right">
                          <span className="font-medium text-blue-600">
                            ${settlement.business_donations.toFixed(2)}
                          </span>
                        </td>
                        <td className="border border-gray-200 px-4 py-3 text-right">
                          <span className="font-bold text-gray-800">
                            ${settlement.total_donations.toFixed(2)}
                          </span>
                        </td>
                        <td className="border border-gray-200 px-4 py-3 text-right">
                          <span className={`font-bold ${settlement.settlement.pending_amount > 0 ? 'text-orange-600' : 'text-gray-400'}`}>
                            ${settlement.settlement.pending_amount.toFixed(2)}
                          </span>
                        </td>
                        <td className="border border-gray-200 px-4 py-3 text-center">
                          {settlement.settlement.pending_amount > 0 ? (
                            <button
                              onClick={() => initiatePayment(settlement.cause.id)}
                              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                            >
                              Initiate Payment
                            </button>
                          ) : (
                            <span className="text-gray-400 text-sm">Settled</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {selectedTab === "analytics" && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Payment Distribution</h3>
                  <div className="space-y-3">
                    {settlements.slice(0, 5).map((settlement) => (
                      <div key={settlement.cause.id} className="flex justify-between items-center">
                        <span className="text-gray-600 truncate max-w-xs">{settlement.cause.name}</span>
                        <span className="font-medium text-gray-800">
                          ${settlement.total_donations.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
                
                <div className="bg-white border border-gray-200 rounded-lg p-4">
                  <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Activity</h3>
                  <div className="space-y-3">
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">System Status:</span> All payment systems operational
                    </div>
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Last Settlement:</span> {
                        settlements.find(s => s.settlement.last_settlement_date)?.settlement.last_settlement_date 
                          ? new Date(settlements.find(s => s.settlement.last_settlement_date).settlement.last_settlement_date).toLocaleDateString()
                          : "No recent settlements"
                      }
                    </div>
                    <div className="text-sm text-gray-600">
                      <span className="font-medium">Pending Causes:</span> {settlements.filter(s => s.settlement.pending_amount > 0).length} causes awaiting payment
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
const DeveloperPlatform = () => {
  const [selectedTab, setSelectedTab] = useState("docs");
  const [apiDocs, setApiDocs] = useState(null);
  const [codeExamples, setCodeExamples] = useState(null);
  const [sdkInfo, setSdkInfo] = useState(null);

  useEffect(() => {
    fetchDeveloperResources();
  }, []);

  const fetchDeveloperResources = async () => {
    try {
      const [docsResponse, examplesResponse, sdkResponse] = await Promise.all([
        axios.get(`${API}/dev/docs`),
        axios.get(`${API}/dev/code-examples`),
        axios.get(`${API}/dev/sdk`)
      ]);
      
      setApiDocs(docsResponse.data);
      setCodeExamples(examplesResponse.data);
      setSdkInfo(sdkResponse.data);
    } catch (error) {
      console.error("Error fetching developer resources:", error);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-3xl font-bold text-gray-800">ImpactLink Developer Platform</h1>
          <p className="text-gray-600 mt-2">Everything you need to integrate social impact into your applications</p>
        </div>

        <div className="p-6">
          <div className="mb-6">
            <div className="flex border-b border-gray-200">
              <button
                onClick={() => setSelectedTab("docs")}
                className={`px-4 py-2 font-medium ${selectedTab === "docs" ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-600"}`}
              >
                API Documentation
              </button>
              <button
                onClick={() => setSelectedTab("examples")}
                className={`px-4 py-2 font-medium ${selectedTab === "examples" ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-600"}`}
              >
                Code Examples
              </button>
              <button
                onClick={() => setSelectedTab("sdks")}
                className={`px-4 py-2 font-medium ${selectedTab === "sdks" ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-600"}`}
              >
                SDKs & Tools
              </button>
              <button
                onClick={() => setSelectedTab("testing")}
                className={`px-4 py-2 font-medium ${selectedTab === "testing" ? "text-blue-600 border-b-2 border-blue-600" : "text-gray-600"}`}
              >
                API Testing
              </button>
            </div>
          </div>

          {selectedTab === "docs" && apiDocs && (
            <div className="space-y-6">
              <div className="bg-blue-50 p-6 rounded-lg">
                <h2 className="text-2xl font-bold text-blue-800 mb-2">{apiDocs.title}</h2>
                <p className="text-blue-700 mb-4">{apiDocs.description}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-semibold">Base URL:</span> {apiDocs.base_url}
                  </div>
                  <div>
                    <span className="font-semibold">Authentication:</span> {apiDocs.authentication.type}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-800">Quick Start</h3>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-700 mb-2">1. Get API Key</h4>
                    <p className="text-sm text-gray-600 mb-3">Register your business and get your API key from the dashboard.</p>
                    
                    <h4 className="font-semibold text-gray-700 mb-2">2. Make Your First Call</h4>
                    <div className="bg-gray-800 text-green-400 p-3 rounded text-sm font-mono">
                      curl -H "Authorization: Bearer YOUR_API_KEY" \\<br/>
                      &nbsp;&nbsp;{apiDocs.base_url}/api/causes
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-xl font-semibold text-gray-800">Rate Limits</h3>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Per Minute:</span>
                        <span className="font-semibold">{apiDocs.rate_limiting?.requests_per_minute || 1000}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Per Day:</span>
                        <span className="font-semibold">{apiDocs.rate_limiting?.requests_per_day || 50000}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-semibold text-gray-800 mb-4">API Endpoints</h3>
                <div className="space-y-4">
                  {Object.entries(apiDocs.endpoints).map(([category, endpoints]) => (
                    <div key={category} className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-semibold text-gray-700 mb-3 capitalize">{category.replace('_', ' ')}</h4>
                      <div className="space-y-2">
                        {Object.entries(endpoints).map(([endpoint, description]) => (
                          <div key={endpoint} className="flex flex-col sm:flex-row sm:justify-between py-2 border-b border-gray-100 last:border-b-0">
                            <code className="text-sm bg-gray-100 px-2 py-1 rounded">{endpoint}</code>
                            <span className="text-sm text-gray-600 mt-1 sm:mt-0">{description}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {selectedTab === "examples" && codeExamples && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-1">
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">Language Examples</h3>
                  <div className="space-y-2">
                    {Object.keys(codeExamples).map((language) => (
                      <button
                        key={language}
                        className="block w-full text-left px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 transition-colors capitalize"
                      >
                        {language}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="lg:col-span-2">
                  <div className="space-y-6">
                    {Object.entries(codeExamples).map(([language, examples]) => (
                      <div key={language} className="border border-gray-200 rounded-lg p-4">
                        <h4 className="text-lg font-semibold text-gray-800 mb-4 capitalize">{language}</h4>
                        
                        <div className="space-y-4">
                          <div>
                            <h5 className="font-medium text-gray-700 mb-2">Installation</h5>
                            <div className="bg-gray-800 text-green-400 p-3 rounded text-sm font-mono relative">
                              <button
                                onClick={() => copyToClipboard(examples.install)}
                                className="absolute top-2 right-2 text-gray-400 hover:text-white"
                              >
                                📋
                              </button>
                              {examples.install}
                            </div>
                          </div>

                          <div>
                            <h5 className="font-medium text-gray-700 mb-2">Setup</h5>
                            <div className="bg-gray-800 text-green-400 p-3 rounded text-sm font-mono relative">
                              <button
                                onClick={() => copyToClipboard(examples.setup)}
                                className="absolute top-2 right-2 text-gray-400 hover:text-white"
                              >
                                📋
                              </button>
                              <pre className="whitespace-pre-wrap">{examples.setup}</pre>
                            </div>
                          </div>

                          {examples.create_transaction && (
                            <div>
                              <h5 className="font-medium text-gray-700 mb-2">Create Transaction</h5>
                              <div className="bg-gray-800 text-green-400 p-3 rounded text-sm font-mono relative">
                                <button
                                  onClick={() => copyToClipboard(examples.create_transaction)}
                                  className="absolute top-2 right-2 text-gray-400 hover:text-white"
                                >
                                  📋
                                </button>
                                <pre className="whitespace-pre-wrap">{examples.create_transaction}</pre>
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {selectedTab === "sdks" && sdkInfo && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(sdkInfo.sdks).map(([language, sdk]) => (
                  <div key={language} className="border border-gray-200 rounded-lg p-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-2 capitalize">{language}</h3>
                    <p className="text-gray-600 mb-4">{sdk.name} v{sdk.version}</p>
                    
                    <div className="space-y-3">
                      <div className="bg-gray-100 p-3 rounded">
                        <code className="text-sm">{sdk.install}</code>
                      </div>
                      
                      <div className="space-y-2">
                        <h4 className="font-medium text-gray-700">Features:</h4>
                        <ul className="text-sm text-gray-600 space-y-1">
                          {sdk.features?.map((feature, index) => (
                            <li key={index}>• {feature}</li>
                          ))}
                        </ul>
                      </div>

                      <div className="flex gap-2">
                        <a href={sdk.docs} className="text-blue-600 hover:text-blue-800 text-sm">Docs</a>
                        <a href={sdk.github} className="text-blue-600 hover:text-blue-800 text-sm">GitHub</a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {sdkInfo.integrations && (
                <div>
                  <h3 className="text-xl font-semibold text-gray-800 mb-4">Platform Integrations</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-gray-700 mb-3">E-commerce Platforms</h4>
                      <div className="space-y-2">
                        {Object.entries(sdkInfo.integrations.e_commerce).map(([platform, url]) => (
                          <div key={platform} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                            <span className="capitalize">{platform}</span>
                            <a href={url} className="text-blue-600 hover:text-blue-800 text-sm">Install</a>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-700 mb-3">Frontend Frameworks</h4>
                      <div className="space-y-2">
                        {Object.entries(sdkInfo.integrations.frameworks).map(([framework, command]) => (
                          <div key={framework} className="p-3 bg-gray-50 rounded">
                            <div className="flex justify-between items-center mb-2">
                              <span className="capitalize font-medium">{framework}</span>
                            </div>
                            <code className="text-sm text-gray-600">{command}</code>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {selectedTab === "testing" && (
            <div className="space-y-6">
              <div className="bg-yellow-50 p-6 rounded-lg">
                <h3 className="text-xl font-semibold text-yellow-800 mb-2">API Testing Environment</h3>
                <p className="text-yellow-700">Test API endpoints directly from your browser with real data.</p>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Interactive Testing</h4>
                  <div className="space-y-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <h5 className="font-medium text-gray-700 mb-2">GET /api/causes</h5>
                      <p className="text-sm text-gray-600 mb-3">Fetch all available causes</p>
                      <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Test Endpoint
                      </button>
                    </div>

                    <div className="border border-gray-200 rounded-lg p-4">
                      <h5 className="font-medium text-gray-700 mb-2">POST /api/transactions</h5>
                      <p className="text-sm text-gray-600 mb-3">Create a new transaction</p>
                      <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Test Endpoint
                      </button>
                    </div>

                    <div className="border border-gray-200 rounded-lg p-4">
                      <h5 className="font-medium text-gray-700 mb-2">POST /api/contributions</h5>
                      <p className="text-sm text-gray-600 mb-3">Create direct contribution</p>
                      <button className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                        Test Endpoint
                      </button>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-lg font-semibold text-gray-800 mb-4">Test Data</h4>
                  <div className="space-y-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <h5 className="font-medium text-gray-700 mb-2">Demo Accounts</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Business:</span>
                          <span className="font-mono">EcoTech Solutions</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Customer:</span>
                          <span className="font-mono">Sarah Green</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Admin:</span>
                          <span className="font-mono">demo_admin</span>
                        </div>
                      </div>
                    </div>

                    <div className="border border-gray-200 rounded-lg p-4">
                      <h5 className="font-medium text-gray-700 mb-2">Test Payment Methods</h5>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Success Card:</span>
                          <span className="font-mono">4242424242424242</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Decline Card:</span>
                          <span className="font-mono">4000000000000002</span>
                        </div>
                      </div>
                    </div>

                    <div className="border border-gray-200 rounded-lg p-4">
                      <h5 className="font-medium text-gray-700 mb-2">Postman Collection</h5>
                      <p className="text-sm text-gray-600 mb-3">Import our complete API collection</p>
                      <button className="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600">
                        Download Collection
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Main App Content Component
function AppContent() {
  const [currentView, setCurrentView] = useState("demo");
  const [business, setBusiness] = useState(null);
  const [recentTransaction, setRecentTransaction] = useState(null);
  const { currentUser, setCurrentUser, userType, setUserType } = useUser();

  const handleUserSelect = (user, type) => {
    setCurrentUser(user);
    setUserType(type);
    if (type === "business") {
      setBusiness(user);
    }
    setCurrentView("home");
  };

  const handleBusinessCreate = (businessData) => {
    setBusiness(businessData);
    setCurrentUser(businessData);
    setUserType("business");
    setCurrentView("dashboard");
  };

  const handleCustomerCreate = (customerData) => {
    setCurrentUser(customerData);
    setUserType("customer");
    setCurrentView("home");
  };

  const renderContent = () => {
    switch (currentView) {
      case "demo":
        return <DemoUserSelector onUserSelect={handleUserSelect} />;
      case "customer-register":
        return <CustomerRegistration onCustomerCreate={handleCustomerCreate} />;
      case "business-setup":
        return <BusinessSetup onBusinessCreate={handleBusinessCreate} />;
      case "dashboard":
        return business ? (
          <BusinessDashboard business={business} />
        ) : (
          <BusinessSetup onBusinessCreate={handleBusinessCreate} />
        );
      case "causes":
        return <CauseBrowser />;
      case "create-cause":
        return currentUser ? <CreateCauseForm /> : <div>Please log in to create a cause</div>;
      case "leaderboards":
        return <LeaderboardSection />;
      case "admin":
        return <AdminDashboard />;
      case "developer":
        return <DeveloperPlatform />;
      case "subscription":
        return currentUser ? (
          <SubscriptionManager userId={currentUser.id} userType={userType} />
        ) : (
          <div className="text-center py-20">Please login to manage subscriptions</div>
        );
      case "settlement":
        return currentUser ? (
          <SettlementManager userId={currentUser.id} userType={userType} />
        ) : (
          <div className="text-center py-20">Please login to manage settlement information</div>
        );
      default:
        return (
          <>
            <HeroSection />
            <FeaturesSection />
            <CauseBrowser />
            <LeaderboardSection />
            <div className="py-20 bg-white text-center">
              <div className="max-w-4xl mx-auto px-4">
                <h2 className="text-4xl font-bold text-gray-800 mb-6">Ready to Make an Impact?</h2>
                <p className="text-xl text-gray-600 mb-8">
                  Join the movement with complete cause management, subscriptions, and settlement tracking.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <button
                    onClick={() => setCurrentView("demo")}
                    className="bg-gradient-to-r from-green-500 to-teal-600 text-white px-12 py-4 rounded-full font-semibold text-xl hover:from-green-600 hover:to-teal-700 transform hover:scale-105 transition-all shadow-xl"
                  >
                    Try Demo Platform
                  </button>
                  <button
                    onClick={() => setCurrentView("business-setup")}
                    className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-12 py-4 rounded-full font-semibold text-xl hover:from-blue-600 hover:to-purple-700 transform hover:scale-105 transition-all shadow-xl"
                  >
                    Register Business
                  </button>
                </div>
              </div>
            </div>
          </>
        );
    }
  };

  return (
    <div className="App">
      {/* Navigation */}
      <nav className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center py-4">
            <div 
              onClick={() => setCurrentView("home")}
              className="flex items-center space-x-2 cursor-pointer"
            >
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-xl">I</span>
              </div>
              <span className="text-2xl font-bold text-gray-800">ImpactLink</span>
            </div>
            
            <div className="flex items-center space-x-6">
              <button
                onClick={() => setCurrentView("home")}
                className={`font-medium transition-colors ${currentView === "home" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
              >
                Home
              </button>
              <button
                onClick={() => setCurrentView("causes")}
                className={`font-medium transition-colors ${currentView === "causes" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
              >
                Causes
              </button>
              {currentUser && (
                <button
                  onClick={() => setCurrentView("create-cause")}
                  className={`font-medium transition-colors ${currentView === "create-cause" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
                >
                  Create Cause
                </button>
              )}
              <button
                onClick={() => setCurrentView("leaderboards")}
                className={`font-medium transition-colors ${currentView === "leaderboards" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
              >
                Leaderboards
              </button>
              <button
                onClick={() => setCurrentView("developer")}
                className={`font-medium transition-colors ${currentView === "developer" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
              >
                Developers
              </button>
              
              {/* User-specific menu */}
              {currentUser && (
                <>
                  <button
                    onClick={() => setCurrentView("subscription")}
                    className={`font-medium transition-colors ${currentView === "subscription" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
                  >
                    Subscription
                  </button>
                </>
              )}
              
              {business && (
                <button
                  onClick={() => setCurrentView("dashboard")}
                  className={`font-medium transition-colors ${currentView === "dashboard" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
                >
                  Dashboard
                </button>
              )}
              
              {/* User Status */}
              {currentUser && (
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <span>Welcome, {currentUser.name || currentUser.username}!</span>
                  {userType === "customer" && <span className="bg-green-100 text-green-800 px-2 py-1 rounded">Contributor</span>}
                  {userType === "business" && <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">Business</span>}
                  {userType === "admin" && <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded">Admin</span>}
                </div>
              )}
              
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentView("demo")}
                  className="bg-green-500 text-white px-4 py-2 rounded-full font-semibold hover:bg-green-600 transition-all"
                >
                  Demo Login
                </button>
                <button
                  onClick={() => setCurrentView("business-setup")}
                  className="bg-blue-500 text-white px-4 py-2 rounded-full font-semibold hover:bg-blue-600 transition-all"
                >
                  Register
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="min-h-screen bg-gray-50">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold">I</span>
                </div>
                <span className="text-xl font-bold">ImpactLink</span>
              </div>
              <p className="text-gray-400 mb-4">
                Complete social impact platform with cause expiration, creator attribution, subscriptions, and settlement management. 
                Demo users available for testing all features.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Demo Access</a></li>
                <li><a href="#" className="hover:text-white">Cause Management</a></li>
                <li><a href="#" className="hover:text-white">Subscriptions</a></li>
                <li><a href="#" className="hover:text-white">Settlement</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li><a href="#" className="hover:text-white">Cause Expiration</a></li>
                <li><a href="#" className="hover:text-white">Creator Links</a></li>
                <li><a href="#" className="hover:text-white">Advanced Filtering</a></li>
                <li><a href="#" className="hover:text-white">Impact Reports</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-700 pt-8 mt-8 text-center">
            <p className="text-gray-500 text-sm">
              © 2025 ImpactLink. All rights reserved. Complete social impact management platform.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

function App() {
  return (
    <UserProvider>
      <AppContent />
    </UserProvider>
  );
}

export default App;