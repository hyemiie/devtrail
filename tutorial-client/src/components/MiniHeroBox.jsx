import React from "react";
import "./miniHero.css";

export const MiniHeroBox = ({ boxDetails }) => {
  return (
    <div className="mini-box">
      <header>hello</header>
      <div className="box-text">
        <h1>Personalized-path angle</h1>
        <p className="box-desc">
          {" "}
          Real LeetCode problems, a built-in IDE, and every solution committed
          straight to your own git history.{" "}
        </p>
        {/* <p className='sub-box-desc'> Automation and full-stack contractor based in Varna</p> */}
        <ul>
          <li>Python</li>
          <li>JavaScript</li>
          <li>Go</li>
        </ul>
        <div className="code-box">
          {}
          <code>hello : "Cape Town ZA"</code>
          <br />
          <code>hello : "Cape Town ZA"</code>
          <br />
          {/* <code>hello : "Cape Town ZA"</code> */}
        </div>
        <p className="code-comment">
          // Built-in checkpoints that keep you moving instead of stalling.

        </p>
      </div>
    </div>
  );
};
