
import {
  createContext,
  useContext,
  useState,
} from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('ais_user');

      return savedUser ? JSON.parse(savedUser) : null;
    } catch (error) {
      console.error('Failed to load user:', error);
      return null;
    }
  });

  const login = (userData) => {
    const loggedInUser = {
      user_id: userData.user_id,
      username: userData.username,
    };

    localStorage.setItem(
      'ais_user',
      JSON.stringify(loggedInUser)
    );

    setUser(loggedInUser);
  };

  const register = (userData) => {
    login(userData);
  };

  const logout = () => {
    localStorage.removeItem('ais_user');
    setUser(null);
  };

  const isAuthenticated = Boolean(user);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error(
      'useAuth must be used inside AuthProvider'
    );
  }

  return context;
}
