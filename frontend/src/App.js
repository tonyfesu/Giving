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
          ImpactLink connects businesses and customers to drive meaningful social change through commerce. 
          Shop with purpose, donate directly, and track your impact in real-time.
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

// Badge Component
const BadgeDisplay = ({ badges, size = "small" }) => {
  const sizeClasses = {
    small: "w-8 h-8 text-sm",
    medium: "w-12 h-12 text-lg",
    large: "w-16 h-16 text-2xl"
  };

  if (!badges || badges.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2">
      {badges.map((badge, index) => (
        <div 
          key={index}
          className={`${sizeClasses[size]} bg-gradient-to-br from-yellow-400 to-yellow-600 rounded-full flex items-center justify-center shadow-lg border-2 border-yellow-300`}
          title={badge.description || `Badge: ${badge}`}
        >
          <span>{badge.icon || badge}</span>
        </div>
      ))}
    </div>
  );
};

// Leaderboard Component
const LeaderboardSection = () => {
  const [businessLeaderboard, setBusinessLeaderboard] = useState([]);
  const [customerLeaderboard, setCustomerLeaderboard] = useState([]);
  const [activeTab, setActiveTab] = useState("businesses");

  useEffect(() => {
    fetchLeaderboards();
  }, []);

  const fetchLeaderboards = async () => {
    try {
      const [businessRes, customerRes] = await Promise.all([
        axios.get(`${API}/leaderboards/businesses`),
        axios.get(`${API}/leaderboards/customers`)
      ]);
      setBusinessLeaderboard(businessRes.data.leaderboard);
      setCustomerLeaderboard(customerRes.data.leaderboard);
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
            Celebrating those making the biggest difference
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
          </div>
        </div>

        <div className="grid md:grid-cols-1 gap-8">
          {activeTab === "businesses" && (
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">
                Businesses by Total Impact
              </h3>
              <div className="space-y-4">
                {businessLeaderboard.map((entry) => (
                  <div key={entry.business.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:shadow-md transition-all">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold ${getRankColor(entry.rank)}`}>
                        {getRankIcon(entry.rank)}
                      </div>
                      <div>
                        <h4 className="font-semibold text-lg text-gray-800">{entry.business.name}</h4>
                        <p className="text-gray-600">{entry.business.industry}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        ${entry.metric_value.toFixed(0)}
                      </div>
                      <div className="text-sm text-gray-500">Total Impact</div>
                      <BadgeDisplay badges={entry.badges} size="small" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "customers" && (
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">
                Top Contributors
              </h3>
              <div className="space-y-4">
                {customerLeaderboard.map((entry) => (
                  <div key={entry.customer.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:shadow-md transition-all">
                    <div className="flex items-center gap-4">
                      <div className={`w-12 h-12 rounded-full flex items-center justify-center font-bold ${getRankColor(entry.rank)}`}>
                        {getRankIcon(entry.rank)}
                      </div>
                      <div>
                        <h4 className="font-semibold text-lg text-gray-800">{entry.customer.name}</h4>
                        <p className="text-gray-600">{entry.customer.contribution_count} contributions</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-600">
                        ${entry.metric_value.toFixed(0)}
                      </div>
                      <div className="text-sm text-gray-500">Total Donated</div>
                      <BadgeDisplay badges={entry.badges} size="small" />
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

// Customer Registration Component
const CustomerRegistration = ({ onCustomerCreate }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: ""
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/customers`, formData);
      onCustomerCreate(response.data);
    } catch (error) {
      console.error("Error creating customer:", error);
      alert("Error creating account: " + (error.response?.data?.detail || error.message));
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="max-w-md mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">Join as a Contributor</h2>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Name *</label>
            <input
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
            <input
              type="email"
              name="email"
              required
              value={formData.email}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
            <input
              type="tel"
              name="phone"
              value={formData.phone}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition-all"
          >
            Create Account & Start Contributing
          </button>
        </form>
      </div>
    </div>
  );
};

// Cause Browser Component
const CauseBrowser = () => {
  const [causes, setCauses] = useState([]);
  const [selectedCause, setSelectedCause] = useState(null);
  const [donationAmount, setDonationAmount] = useState("");
  const [message, setMessage] = useState("");
  const { currentUser } = useUser();

  useEffect(() => {
    fetchCauses();
  }, []);

  const fetchCauses = async () => {
    try {
      const response = await axios.get(`${API}/causes`);
      setCauses(response.data);
    } catch (error) {
      console.error("Error fetching causes:", error);
    }
  };

  const handleDonate = async () => {
    if (!currentUser) {
      alert("Please register as a customer first to make donations");
      return;
    }

    try {
      const contributionData = {
        customer_id: currentUser.id,
        cause_id: selectedCause.id,
        amount: parseFloat(donationAmount),
        message: message || undefined,
        anonymous: false
      };

      await axios.post(`${API}/contributions`, contributionData);
      alert(`Thank you! Your $${donationAmount} donation will help ${selectedCause.name}`);
      setSelectedCause(null);
      setDonationAmount("");
      setMessage("");
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

  return (
    <div className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Support a Cause You Care About
          </h2>
          <p className="text-xl text-gray-600">
            Make a direct impact on the causes that matter most to you
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {causes.map((cause) => (
            <div key={cause.id} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-all">
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
                </div>
                
                <h3 className="text-xl font-bold text-gray-800 mb-2">{cause.name}</h3>
                <p className="text-gray-600 mb-4 text-sm">{cause.description}</p>
                
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

                <div className="mb-4 text-sm text-gray-600">
                  <p><strong>Impact:</strong> ${cause.cost_per_impact} per {cause.impact_metric}</p>
                  <p><strong>Total Impact:</strong> {cause.total_impact_units.toFixed(0)} {cause.impact_metric}</p>
                </div>

                <button
                  onClick={() => setSelectedCause(cause)}
                  className="w-full bg-blue-500 text-white py-3 rounded-lg font-semibold hover:bg-blue-600 transition-all"
                >
                  Donate Now
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Donation Modal */}
        {selectedCause && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl p-8 max-w-md w-full">
              <h3 className="text-2xl font-bold text-gray-800 mb-4">
                Donate to {selectedCause.name}
              </h3>
              
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
                  disabled={!donationAmount || !currentUser}
                  className="flex-1 bg-green-500 text-white py-3 rounded-lg font-semibold hover:bg-green-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                >
                  {currentUser ? "Donate Now" : "Register to Donate"}
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

// Admin Dashboard Component
const AdminDashboard = () => {
  const [adminData, setAdminData] = useState(null);
  const [businesses, setBusinesses] = useState([]);
  const [causes, setCauses] = useState([]);
  const [activeTab, setActiveTab] = useState("overview");

  useEffect(() => {
    fetchAdminData();
    fetchBusinesses();
    fetchCauses();
  }, []);

  const fetchAdminData = async () => {
    try {
      const response = await axios.get(`${API}/admin/dashboard`);
      setAdminData(response.data);
    } catch (error) {
      console.error("Error fetching admin data:", error);
    }
  };

  const fetchBusinesses = async () => {
    try {
      const response = await axios.get(`${API}/admin/businesses`);
      setBusinesses(response.data);
    } catch (error) {
      console.error("Error fetching businesses:", error);
    }
  };

  const fetchCauses = async () => {
    try {
      const response = await axios.get(`${API}/admin/causes`);
      setCauses(response.data);
    } catch (error) {
      console.error("Error fetching causes:", error);
    }
  };

  const verifyBusiness = async (businessId) => {
    try {
      await axios.put(`${API}/admin/businesses/${businessId}/verify`);
      alert("Business verified successfully!");
      fetchBusinesses();
    } catch (error) {
      console.error("Error verifying business:", error);
      alert("Error verifying business");
    }
  };

  if (!adminData) {
    return <div className="flex justify-center items-center h-64">Loading admin dashboard...</div>;
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-2">Platform Administration</h1>
        <p className="text-gray-600">Manage businesses, causes, and monitor platform activity</p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-4 mb-8">
        {[
          { id: "overview", label: "Overview" },
          { id: "businesses", label: "Businesses" },
          { id: "causes", label: "Causes" },
          { id: "activity", label: "Recent Activity" }
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-6 py-3 rounded-lg font-semibold transition-all ${
              activeTab === tab.id
                ? "bg-blue-500 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === "overview" && (
        <div className="space-y-8">
          {/* Statistics Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total Businesses</h3>
              <p className="text-3xl font-bold text-blue-600">{adminData.statistics.total_businesses}</p>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total Customers</h3>
              <p className="text-3xl font-bold text-green-600">{adminData.statistics.total_customers}</p>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Active Causes</h3>
              <p className="text-3xl font-bold text-purple-600">{adminData.statistics.total_causes}</p>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Platform Impact</h3>
              <p className="text-3xl font-bold text-red-600">${adminData.statistics.total_platform_impact.toFixed(0)}</p>
            </div>
          </div>

          {/* Top Causes */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Top Performing Causes</h3>
            <div className="space-y-4">
              {adminData.top_causes.map((cause) => (
                <div key={cause.id} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                  <div>
                    <h4 className="font-semibold text-gray-800">{cause.name}</h4>
                    <p className="text-sm text-gray-600">{cause.category}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-green-600">${cause.total_raised.toFixed(0)}</p>
                    <p className="text-sm text-gray-500">{cause.total_impact_units.toFixed(0)} {cause.impact_metric}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Businesses Tab */}
      {activeTab === "businesses" && (
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6">Business Management</h3>
          <div className="space-y-4">
            {businesses.map((business) => (
              <div key={business.id} className="flex justify-between items-center p-4 border border-gray-200 rounded-lg">
                <div>
                  <h4 className="font-semibold text-gray-800 flex items-center gap-2">
                    {business.name}
                    {business.verified && <span className="text-green-500">✓</span>}
                    <BadgeDisplay badges={business.badges} size="small" />
                  </h4>
                  <p className="text-sm text-gray-600">{business.industry} • {business.email}</p>
                  <p className="text-sm text-gray-500">
                    Total Impact: ${business.total_impact.toFixed(0)} • Transactions: {business.transaction_count}
                  </p>
                </div>
                <div className="flex gap-2">
                  {!business.verified && (
                    <button
                      onClick={() => verifyBusiness(business.id)}
                      className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-all"
                    >
                      Verify
                    </button>
                  )}
                  <button className="px-4 py-2 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-200 transition-all">
                    View Details
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Causes Tab */}
      {activeTab === "causes" && (
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-800 mb-6">Cause Management</h3>
          <div className="grid md:grid-cols-2 gap-6">
            {causes.map((cause) => (
              <div key={cause.id} className="p-6 border border-gray-200 rounded-lg">
                <div className="flex justify-between items-start mb-4">
                  <h4 className="font-semibold text-gray-800">{cause.name}</h4>
                  <div className="flex gap-2">
                    {cause.active && <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Active</span>}
                    {cause.featured && <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">Featured</span>}
                  </div>
                </div>
                <p className="text-sm text-gray-600 mb-3">{cause.description}</p>
                <div className="text-sm text-gray-500 space-y-1">
                  <p>Category: {cause.category}</p>
                  <p>Total Raised: ${cause.total_raised.toFixed(0)}</p>
                  <p>Impact Units: {cause.total_impact_units.toFixed(0)} {cause.impact_metric}</p>
                  {cause.goal_amount && <p>Goal: ${cause.goal_amount.toFixed(0)}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity Tab */}
      {activeTab === "activity" && (
        <div className="space-y-8">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Recent Transactions</h3>
            <div className="space-y-3">
              {adminData.recent_activity.transactions.map((transaction) => (
                <div key={transaction.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">Transaction: ${transaction.amount}</p>
                    <p className="text-sm text-gray-600">Impact: ${transaction.total_impact_amount.toFixed(2)}</p>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(transaction.timestamp).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6">Recent Contributions</h3>
            <div className="space-y-3">
              {adminData.recent_activity.contributions.map((contribution) => (
                <div key={contribution.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-medium">Donation: ${contribution.amount}</p>
                    <p className="text-sm text-gray-600">Impact: {contribution.impact_units.toFixed(1)} units</p>
                  </div>
                  <div className="text-sm text-gray-500">
                    {new Date(contribution.timestamp).toLocaleDateString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Business Dashboard Component (Enhanced with badges)
const BusinessDashboard = ({ business, onTransactionCreate }) => {
  const [causes, setCauses] = useState([]);
  const [allocations, setAllocations] = useState({});
  const [dashboard, setDashboard] = useState(null);
  const [transactionAmount, setTransactionAmount] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [showTransactionForm, setShowTransactionForm] = useState(false);

  useEffect(() => {
    if (business?.id) {
      fetchCauses();
      fetchDashboard();
      setAllocations(business.impact_allocations || {});
    }
  }, [business]);

  const fetchCauses = async () => {
    try {
      const response = await axios.get(`${API}/causes`);
      setCauses(response.data);
    } catch (error) {
      console.error("Error fetching causes:", error);
    }
  };

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API}/impact/dashboard/${business.id}`);
      setDashboard(response.data);
    } catch (error) {
      console.error("Error fetching dashboard:", error);
    }
  };

  const handleAllocationChange = (causeId, percentage) => {
    setAllocations(prev => ({
      ...prev,
      [causeId]: percentage
    }));
  };

  const saveAllocations = async () => {
    try {
      const allocationList = Object.entries(allocations)
        .filter(([_, percentage]) => percentage > 0)
        .map(([cause_id, percentage]) => ({ cause_id, percentage: parseFloat(percentage) }));

      await axios.put(`${API}/businesses/${business.id}/impact-allocation`, allocationList);
      alert("Impact allocation saved successfully!");
      fetchDashboard();
    } catch (error) {
      console.error("Error saving allocations:", error);
      alert("Error saving allocations: " + (error.response?.data?.detail || error.message));
    }
  };

  const createTransaction = async () => {
    try {
      const transaction = {
        business_id: business.id,
        amount: parseFloat(transactionAmount),
        customer_name: customerName || undefined
      };

      const response = await axios.post(`${API}/transactions`, transaction);
      alert(`Transaction created! Impact: $${response.data.total_impact_amount.toFixed(2)}`);
      setTransactionAmount("");
      setCustomerName("");
      setShowTransactionForm(false);
      fetchDashboard();
      if (onTransactionCreate) onTransactionCreate(response.data);
    } catch (error) {
      console.error("Error creating transaction:", error);
      alert("Error creating transaction: " + (error.response?.data?.detail || error.message));
    }
  };

  const totalPercentage = Object.values(allocations).reduce((sum, val) => sum + (parseFloat(val) || 0), 0);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
        <div className="flex justify-between items-center mb-6">
          <div className="flex items-center gap-4">
            <div>
              <h2 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
                {business.name}
                {business.verified && <span className="text-green-500" title="Verified Business">✓</span>}
              </h2>
              <p className="text-gray-600">{business.description}</p>
              <div className="mt-2">
                <BadgeDisplay badges={dashboard?.badges || []} size="medium" />
              </div>
            </div>
          </div>
          <div className="flex gap-4">
            <div className="text-center">
              <div className="text-sm text-gray-500">API Key</div>
              <div className="text-xs font-mono bg-gray-100 p-2 rounded">
                {business.api_key}
              </div>
            </div>
            <button
              onClick={() => setShowTransactionForm(!showTransactionForm)}
              className="bg-green-500 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-600 transition-all"
            >
              + New Transaction
            </button>
          </div>
        </div>

        {/* Transaction Form */}
        {showTransactionForm && (
          <div className="bg-gray-50 rounded-lg p-6 mb-6">
            <h3 className="text-xl font-semibold mb-4">Create New Transaction</h3>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Transaction Amount ($)</label>
                <input
                  type="number"
                  value={transactionAmount}
                  onChange={(e) => setTransactionAmount(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="0.00"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Customer Name (Optional)</label>
                <input
                  type="text"
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Customer name"
                />
              </div>
            </div>
            <div className="mt-4 flex gap-4">
              <button
                onClick={createTransaction}
                disabled={!transactionAmount}
                className="bg-blue-500 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Create Transaction
              </button>
              <button
                onClick={() => setShowTransactionForm(false)}
                className="bg-gray-300 text-gray-700 px-6 py-2 rounded-lg font-semibold hover:bg-gray-400"
              >
                Cancel
              </button>
            </div>
          </div>
        )}

        {/* Impact Statistics */}
        {dashboard && (
          <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-blue-600">${dashboard.total_sales.toFixed(2)}</h3>
              <p className="text-blue-800 font-medium">Total Sales</p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-green-600">${dashboard.total_impact.toFixed(2)}</h3>
              <p className="text-green-800 font-medium">Total Impact</p>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-purple-600">{dashboard.impact_percentage.toFixed(1)}%</h3>
              <p className="text-purple-800 font-medium">Impact Rate</p>
            </div>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-6 text-center">
              <h3 className="text-2xl font-bold text-orange-600">{business.transaction_count}</h3>
              <p className="text-orange-800 font-medium">Transactions</p>
            </div>
          </div>
        )}
      </div>

      {/* Impact Allocation Setup */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h3 className="text-2xl font-bold text-gray-800 mb-6">Impact Allocation Setup</h3>
        <p className="text-gray-600 mb-6">
          Choose which social causes you want to support and what percentage of each sale should go to each cause.
        </p>

        <div className="space-y-4 mb-6">
          {causes.map((cause) => (
            <div key={cause.id} className="border border-gray-200 rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-800">{cause.name}</h4>
                  <p className="text-gray-600 mb-2">{cause.description}</p>
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span className="bg-gray-100 px-3 py-1 rounded-full">{cause.category}</span>
                    <span>${cause.cost_per_impact} per {cause.impact_metric}</span>
                    {cause.featured && <span className="text-yellow-600">⭐ Featured</span>}
                  </div>
                </div>
                <div className="ml-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Percentage</label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min="0"
                      max="100"
                      step="0.1"
                      value={allocations[cause.id] || ""}
                      onChange={(e) => handleAllocationChange(cause.id, e.target.value)}
                      className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    <span className="text-gray-500">%</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="flex justify-between items-center">
          <div className="text-lg">
            <span className="text-gray-700">Total Allocation: </span>
            <span className={`font-bold ${totalPercentage > 100 ? 'text-red-600' : 'text-green-600'}`}>
              {totalPercentage.toFixed(1)}%
            </span>
            {totalPercentage > 100 && (
              <span className="text-red-600 text-sm ml-2">Cannot exceed 100%</span>
            )}
          </div>
          <button
            onClick={saveAllocations}
            disabled={totalPercentage > 100}
            className="bg-blue-500 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          >
            Save Allocation
          </button>
        </div>
      </div>
    </div>
  );
};

// Business Setup Component (Enhanced)
const BusinessSetup = ({ onBusinessCreate }) => {
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    industry: "",
    email: "",
    phone: "",
    website: ""
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API}/businesses`, formData);
      onBusinessCreate(response.data);
    } catch (error) {
      console.error("Error creating business:", error);
      alert("Error creating business: " + (error.response?.data?.detail || error.message));
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-6 text-center">Setup Your Business</h2>
        <p className="text-gray-600 mb-8 text-center">
          Join ImpactLink and start integrating social impact into your business operations!
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Business Name *</label>
            <input
              type="text"
              name="name"
              required
              value={formData.name}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Your Business Name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description *</label>
            <textarea
              name="description"
              required
              value={formData.description}
              onChange={handleChange}
              rows="3"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Brief description of your business"
            />
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Industry *</label>
              <select
                name="industry"
                required
                value={formData.industry}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Industry</option>
                <option value="Retail">Retail</option>
                <option value="E-commerce">E-commerce</option>
                <option value="Food & Beverage">Food & Beverage</option>
                <option value="Technology">Technology</option>
                <option value="Services">Services</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Education">Education</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Email *</label>
              <input
                type="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="business@example.com"
              />
            </div>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Phone</label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Website</label>
              <input
                type="url"
                name="website"
                value={formData.website}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="https://yourwebsite.com"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full bg-blue-500 text-white py-4 rounded-lg font-semibold text-lg hover:bg-blue-600 transform hover:scale-105 transition-all shadow-lg"
          >
            Create Business & Start Making Impact
          </button>
        </form>
      </div>
    </div>
  );
};

// Features Section Component
const FeaturesSection = () => {
  const features = [
    {
      title: "Impact Allocation Engine",
      description: "Choose causes you care about and set what percentage of each sale goes to social impact",
      icon: "🎯",
      color: "bg-green-100 border-green-200"
    },
    {
      title: "Real-time Impact Tracking",
      description: "See exactly how much impact your business is creating with transparent, real-time dashboards",
      icon: "📊",
      color: "bg-blue-100 border-blue-200"
    },
    {
      title: "Direct Contributions",
      description: "Customers can donate directly to causes they care about, creating additional impact streams",
      icon: "💝",
      color: "bg-purple-100 border-purple-200"
    },
    {
      title: "Leaderboards & Badges",
      description: "Gamified impact tracking with achievements, badges, and community recognition",
      icon: "🏆",
      color: "bg-yellow-100 border-yellow-200"
    },
    {
      title: "API Integration",
      description: "Seamlessly integrate ImpactLink into existing e-commerce platforms and POS systems",
      icon: "🔗",
      color: "bg-red-100 border-red-200"
    },
    {
      title: "Admin Dashboard",
      description: "Comprehensive platform management tools for monitoring activity and managing causes",
      icon: "⚙️",
      color: "bg-gray-100 border-gray-200"
    }
  ];

  return (
    <div className="py-20 px-4 bg-gray-50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-800 mb-4">
            Complete Social Impact Platform
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Everything you need to integrate social responsibility into your business operations
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

// Main App Component
function AppContent() {
  const [currentView, setCurrentView] = useState("home");
  const [business, setBusiness] = useState(null);
  const [recentTransaction, setRecentTransaction] = useState(null);
  const { currentUser, setCurrentUser, userType, setUserType } = useUser();

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

  const handleTransactionCreate = (transactionData) => {
    setRecentTransaction(transactionData);
  };

  const renderContent = () => {
    switch (currentView) {
      case "customer-register":
        return <CustomerRegistration onCustomerCreate={handleCustomerCreate} />;
      case "business-setup":
        return <BusinessSetup onBusinessCreate={handleBusinessCreate} />;
      case "dashboard":
        return business ? (
          <BusinessDashboard business={business} onTransactionCreate={handleTransactionCreate} />
        ) : (
          <BusinessSetup onBusinessCreate={handleBusinessCreate} />
        );
      case "causes":
        return <CauseBrowser />;
      case "leaderboards":
        return <LeaderboardSection />;
      case "admin":
        return <AdminDashboard />;
      default:
        return (
          <>
            <HeroSection />
            <FeaturesSection />
            <LeaderboardSection />
            <CauseBrowser />
            <div className="py-20 bg-white text-center">
              <div className="max-w-4xl mx-auto px-4">
                <h2 className="text-4xl font-bold text-gray-800 mb-6">Ready to Make an Impact?</h2>
                <p className="text-xl text-gray-600 mb-8">
                  Join the movement of businesses and individuals creating positive social change through commerce.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <button
                    onClick={() => setCurrentView("business-setup")}
                    className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-12 py-4 rounded-full font-semibold text-xl hover:from-blue-600 hover:to-purple-700 transform hover:scale-105 transition-all shadow-xl"
                  >
                    Register as Business
                  </button>
                  <button
                    onClick={() => setCurrentView("customer-register")}
                    className="bg-gradient-to-r from-green-500 to-teal-600 text-white px-12 py-4 rounded-full font-semibold text-xl hover:from-green-600 hover:to-teal-700 transform hover:scale-105 transition-all shadow-xl"
                  >
                    Join as Contributor
                  </button>
                </div>
              </div>
            </div>
          </>
        );
    }
  };

  return (
    <UserProvider>
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
                {business && (
                  <button
                    onClick={() => setCurrentView("dashboard")}
                    className={`font-medium transition-colors ${currentView === "dashboard" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
                  >
                    Dashboard
                  </button>
                )}
                <button
                  onClick={() => setCurrentView("admin")}
                  className={`font-medium transition-colors ${currentView === "admin" ? "text-blue-600" : "text-gray-600 hover:text-blue-600"}`}
                >
                  Admin
                </button>
                
                {/* User Status */}
                {currentUser && (
                  <div className="flex items-center gap-2 text-sm text-gray-600">
                    <span>Welcome, {currentUser.name}!</span>
                    {userType === "customer" && <span className="bg-green-100 text-green-800 px-2 py-1 rounded">Contributor</span>}
                    {userType === "business" && <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded">Business</span>}
                  </div>
                )}
                
                <div className="flex gap-2">
                  <button
                    onClick={() => setCurrentView("business-setup")}
                    className="bg-blue-500 text-white px-4 py-2 rounded-full font-semibold hover:bg-blue-600 transition-all"
                  >
                    {business ? "New Business" : "For Business"}
                  </button>
                  <button
                    onClick={() => setCurrentView("customer-register")}
                    className="bg-green-500 text-white px-4 py-2 rounded-full font-semibold hover:bg-green-600 transition-all"
                  >
                    Contribute
                  </button>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Recent Transaction Success Alert */}
        {recentTransaction && (
          <div className="bg-green-50 border-l-4 border-green-400 p-4 m-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-green-700">
                  <strong>Transaction Created Successfully!</strong> Impact Amount: ${recentTransaction.total_impact_amount.toFixed(2)}
                </p>
                <button
                  onClick={() => setRecentTransaction(null)}
                  className="text-green-600 hover:text-green-800 text-sm underline ml-2"
                >
                  Dismiss
                </button>
              </div>
            </div>
          </div>
        )}

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
                  Empowering businesses and individuals to drive social change through commerce. 
                  Together, we're building a better world, one transaction at a time.
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold mb-4">Platform</h4>
                <ul className="space-y-2 text-gray-400">
                  <li><a href="#" className="hover:text-white">For Businesses</a></li>
                  <li><a href="#" className="hover:text-white">For Contributors</a></li>
                  <li><a href="#" className="hover:text-white">API Documentation</a></li>
                  <li><a href="#" className="hover:text-white">Support</a></li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold mb-4">Impact</h4>
                <ul className="space-y-2 text-gray-400">
                  <li><a href="#" className="hover:text-white">Browse Causes</a></li>
                  <li><a href="#" className="hover:text-white">Leaderboards</a></li>
                  <li><a href="#" className="hover:text-white">Success Stories</a></li>
                  <li><a href="#" className="hover:text-white">Impact Reports</a></li>
                </ul>
              </div>
            </div>
            
            <div className="border-t border-gray-700 pt-8 mt-8 text-center">
              <p className="text-gray-500 text-sm">
                © 2025 ImpactLink. All rights reserved. Building a better world through commerce.
              </p>
            </div>
          </div>
        </footer>
      </div>
    </UserProvider>
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