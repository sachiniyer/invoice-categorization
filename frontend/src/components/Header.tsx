import React from 'react';

const Header: React.FC = () => {
    return (
        <header className="bg-blue-500 p-4">
            <nav className="flex justify-between items-center">
                <div className="text-white font-bold text-xl"><a href="/">Invoice Categorization</a></div>
                <a className='text-white' href="/user">Profile</a>
            </nav>
        </header>
    );
};

export default Header;
