import React, {
  createContext,
  useContext,
  useState,
  ReactNode,
  useEffect,
} from "react";
import { User } from "../types/user";
import {
  register_user,
  login_user,
  verify_token,
  update_password,
  delete_user,
} from "../api/user";
import Cookies from "js-cookie";

interface UserContextType {
  user: User | null;
  loaded: boolean;
  login: (userData: User) => boolean;
  register: (userData: User) => boolean;
  update: (password: string) => boolean;
  del: () => boolean;
  logout: () => boolean;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [loaded, setLoaded] = useState<boolean>(false);

  const load_cookies = async () => {
    if (
      process.env.REACT_APP_USERNAME_COOKIE !== undefined &&
      process.env.REACT_APP_TOKEN_COOKIE !== undefined
    ) {
      let username = Cookies.get(process.env.REACT_APP_USERNAME_COOKIE);
      let token = Cookies.get(process.env.REACT_APP_TOKEN_COOKIE);
      if (
        username !== undefined &&
        token !== undefined &&
        process.env.REACT_APP_HAPI !== undefined
      ) {
        let userData: User = {
          username: username,
          password: "",
          token: token,
        };
        verify_token(token, process.env.REACT_APP_HAPI)
          .then((_) => {
            setUser(userData);
          })
          .catch((_) => {
            setUser(null);
          });
      } else {
        setUser(null);
      }
      setLoaded(true);
    }
  };

  useEffect(() => {
    load_cookies();
  }, []);

  const set_cookies = (userData: User) => {
    if (
      userData.username !== null &&
      userData.username !== undefined &&
      userData.token !== null &&
      userData.token !== undefined &&
      process.env.REACT_APP_USERNAME_COOKIE !== undefined &&
      process.env.REACT_APP_TOKEN_COOKIE !== undefined
    ) {
      Cookies.set(process.env.REACT_APP_USERNAME_COOKIE, userData.username, {
        sameSite: "strict",
      });
      Cookies.set(process.env.REACT_APP_TOKEN_COOKIE, userData.token, {
        sameSite: "strict",
      });
    }
  };

  const delete_cookies = () => {
    if (
      process.env.REACT_APP_USERNAME_COOKIE !== undefined &&
      process.env.REACT_APP_TOKEN_COOKIE !== undefined
    ) {
      Cookies.remove(process.env.REACT_APP_USERNAME_COOKIE);
      Cookies.remove(process.env.REACT_APP_TOKEN_COOKIE);
    }
  };

  const login = (userData: User) => {
    try {
      if (
        userData !== null &&
        userData.username !== null &&
        userData.password !== null &&
        process.env.REACT_APP_HAPI !== undefined
      ) {
        login_user(
          userData.username,
          userData.password,
          process.env.REACT_APP_HAPI
        ).then((response) => {
          userData.token = response.jwt;
          console.log(userData);
          setUser(userData);
          set_cookies(userData);
        });
      } else {
        throw new Error("Username and password are required");
      }
    } catch (e) {
      return false;
    }
    return true;
  };

  const register = (userData: User) => {
    try {
      if (
        userData !== null &&
        userData.username !== null &&
        userData.password !== null &&
        process.env.REACT_APP_HAPI !== undefined
      ) {
        register_user(
          userData.username,
          userData.password,
          process.env.REACT_APP_HAPI
        ).then((_) => {
          login(userData);
          return true;
        });
      } else {
        throw new Error("Username and password are required");
      }
    } catch (e) {
      return false;
    }
    return false;
  };

  const update = (password: string) => {
    try {
      if (
        user !== null &&
        user.username !== null &&
        user.token !== null &&
        process.env.REACT_APP_HAPI !== undefined
      ) {
        update_password(
          user.username,
          password,
          user.token,
          process.env.REACT_APP_HAPI
        ).then((response) => {
          let newUserData: User = {
            username: user.username,
            password: password,
            token: response.jwt,
          };
          setUser(newUserData);
          set_cookies(newUserData);
          return true;
        });
      } else {
        throw new Error("User is not logged in");
      }
    } catch (e) {
      return false;
    }
    return false;
  };

  const del = () => {
    try {
      if (
        user !== null &&
        user.username !== null &&
        user.token !== null &&
        process.env.REACT_APP_HAPI !== undefined
      ) {
        delete_user(user.username, user.token, process.env.REACT_APP_HAPI).then(
          (_) => {
            logout();
            return true;
          }
        );
      } else {
        throw new Error("User is not logged in");
      }
    } catch (e) {
      return false;
    }
    return false;
  };

  const logout = () => {
    setUser(null);
    delete_cookies();
    return true;
  };

  return (
    <UserContext.Provider
      value={{ user, loaded, login, register, update, del, logout }}
    >
      {children}
    </UserContext.Provider>
  );
};

export const useUserContext = (): UserContextType => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error("useUserContext must be used within a UserProvider");
  }
  return context;
};
