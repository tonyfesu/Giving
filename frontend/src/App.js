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
  const { currentUser } = useUser();

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
    } catch (error) {
      console.error("Error fetching causes:", error);
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
const BusinessDashboard = ({ business }) => <div></div>;
const AdminDashboard = () => <div></div>;
const DeveloperPlatform = () => <div></div>;

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
                  <button
                    onClick={() => setCurrentView("settlement")}
                    className={`font-medium transition-colors ${currentView === "settlement" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
                  >
                    Settlement
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