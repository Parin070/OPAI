import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Upload, LogOut, Loader2, Settings } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ClothingItem {
  id: string;
  image_url: string;
  category: string;
  color: string;
  pattern: string;
  season: string;
  formality_score: number | null;
}

interface User {
  id: string;
  email: string;
  body_type: string | null;
}

const BODY_TYPES = ["Slim", "Athletic", "Average", "Broad", "Plus-size"];

export const Wardrobe = () => {
  const { token, logout } = useAuth();
  const [items, setItems] = useState<ClothingItem[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [showBodyTypeModal, setShowBodyTypeModal] = useState(false);
  const [updatingBodyType, setUpdatingBodyType] = useState(false);

  const fetchItemsAndUser = async () => {
    try {
      // Fetch User
      const userRes = await fetch(`${API_URL}/users/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!userRes.ok) throw new Error('Failed to fetch user');
      const userData = await userRes.json();
      setUser(userData);

      // Force onboarding if body_type is missing
      if (!userData.body_type) {
        setShowBodyTypeModal(true);
      }

      // Fetch Items
      const itemsRes = await fetch(`${API_URL}/items`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!itemsRes.ok) throw new Error('Failed to fetch items');
      const itemsData = await itemsRes.json();
      setItems(itemsData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchItemsAndUser();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    setError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/items/upload`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      
      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || 'Upload failed');
      }
      
      // Refresh items after upload
      const itemsRes = await fetch(`${API_URL}/items`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (itemsRes.ok) {
        const itemsData = await itemsRes.json();
        setItems(itemsData);
      }
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleUpdateBodyType = async (bodyType: string) => {
    setUpdatingBodyType(true);
    setError('');
    try {
      const res = await fetch(`${API_URL}/users/me`, {
        method: 'PATCH',
        headers: { 
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ body_type: bodyType })
      });
      
      if (!res.ok) throw new Error('Failed to update body type');
      
      const updatedUser = await res.json();
      setUser(updatedUser);
      setShowBodyTypeModal(false);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setUpdatingBodyType(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Body Type Modal Overlay */}
      {showBodyTypeModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50 px-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-lg w-full p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome to StyleSync!</h2>
            <p className="text-gray-600 mb-6">
              To give you the best outfit recommendations, please select your body type.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-6">
              {BODY_TYPES.map((bt) => (
                <button
                  key={bt}
                  disabled={updatingBodyType}
                  onClick={() => handleUpdateBodyType(bt)}
                  className={`py-3 px-4 rounded-lg border-2 text-sm font-medium transition-colors
                    ${user?.body_type === bt 
                      ? 'border-indigo-600 bg-indigo-50 text-indigo-700' 
                      : 'border-gray-200 text-gray-700 hover:border-indigo-300 hover:bg-gray-50'
                    } disabled:opacity-50`}
                >
                  {bt}
                </button>
              ))}
            </div>
            {/* If user already has a body type (e.g. opened via settings), let them close it */}
            {user?.body_type && (
              <button
                onClick={() => setShowBodyTypeModal(false)}
                className="w-full py-2 px-4 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
            )}
          </div>
        </div>
      )}

      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold text-gray-900">StyleSync Wardrobe</h1>
            <div className="flex items-center space-x-6">
              {user?.body_type && (
                <button
                  onClick={() => setShowBodyTypeModal(true)}
                  className="flex items-center text-gray-500 hover:text-gray-900 transition-colors text-sm font-medium"
                  title="Update Body Type"
                >
                  <Settings className="w-5 h-5 mr-1.5" />
                  {user.body_type}
                </button>
              )}
              <button
                onClick={logout}
                className="flex items-center text-gray-500 hover:text-gray-900 transition-colors text-sm font-medium"
              >
                <LogOut className="w-5 h-5 mr-1.5" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-white hover:bg-gray-50 transition-colors">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              {uploading ? (
                <Loader2 className="w-8 h-8 text-indigo-500 animate-spin mb-2" />
              ) : (
                <Upload className="w-8 h-8 text-gray-400 mb-2" />
              )}
              <p className="text-sm text-gray-500">
                {uploading ? 'Analyzing with AI...' : 'Click to upload a clothing item'}
              </p>
            </div>
            <input 
              type="file" 
              className="hidden" 
              accept="image/*" 
              onChange={handleFileUpload}
              disabled={uploading}
            />
          </label>
          {error && <p className="mt-2 text-sm text-red-600 text-center">{error}</p>}
        </div>

        {loading ? (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {items.map((item) => (
              <div key={item.id} className="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-100 transition-transform hover:scale-[1.02]">
                <div className="aspect-[4/5] relative bg-gray-100">
                  <img
                    src={item.image_url}
                    alt={item.category}
                    className="absolute inset-0 w-full h-full object-cover"
                  />
                </div>
                <div className="p-4">
                  <h3 className="text-lg font-semibold text-gray-900 capitalize mb-2">
                    {item.category || 'Unknown Item'}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {item.color && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                        {item.color}
                      </span>
                    )}
                    {item.pattern && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 capitalize">
                        {item.pattern}
                      </span>
                    )}
                    {item.season && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 capitalize">
                        {item.season}
                      </span>
                    )}
                    {item.formality_score !== null && item.formality_score !== undefined && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        Formality: {item.formality_score}/10
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {items.length === 0 && !error && (
              <div className="col-span-full text-center py-12 text-gray-500">
                Your wardrobe is empty. Upload some clothes to get started!
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};
