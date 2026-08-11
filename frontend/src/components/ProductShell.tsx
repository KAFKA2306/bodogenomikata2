import React from 'react';
import { Link, NavLink } from 'react-router-dom';

type ProductShellProps = {
  children: React.ReactNode;
  mainId?: string;
};

export const ProductShell: React.FC<ProductShellProps> = ({ children, mainId = 'main-content' }) => (
  <div className="product-shell">
    <a className="workflow-skip-link" href={`#${mainId}`}>本文へ移動</a>
    <header className="product-header">
      <Link to="/" className="product-brand" aria-label="ボドゲのミカタ ホーム">
        <span className="product-brand-mark" aria-hidden="true">見</span>
        <span><strong>ボドゲのミカタ</strong><small>出典付きボードゲーム補助</small></span>
      </Link>
      <nav className="mode-navigation" aria-label="利用モード">
        <NavLink to="/play" className={({ isActive }) => isActive ? 'mode-link active' : 'mode-link'}>プレイ中</NavLink>
        <NavLink to="/install" className={({ isActive }) => isActive ? 'mode-link active' : 'mode-link'}>開始前</NavLink>
        <NavLink to="/research" className={({ isActive }) => isActive ? 'mode-link active' : 'mode-link'}>作品・調査</NavLink>
        <NavLink to="/cards/palworld" className={({ isActive }) => isActive ? 'mode-link active' : 'mode-link'}>カードDB</NavLink>
      </nav>
    </header>
    <main id={mainId}>{children}</main>
    <footer className="product-footer">
      <span>公式ルール・抽出事実・AI要約・翻訳・レビューを区別します。</span>
      <span>根拠不足時は回答しません。</span>
    </footer>
  </div>
);
