import React from 'react'
import './heroBox.css'

export const HeroBox = ({boxDetails}) => {
  return (
    <div className='box'>

        <header>hello</header>
        <div className='box-text'>
        <h1>Simplicity</h1>
        <p className='box-desc'> Diagnostic quiz, curriculum, IDE, and AI guidance </p>
        <p className='sub-box-desc'> Every lesson, quiz, and weekly project ends up as a real commit</p>
        <ul>
        
            <li>Python</li>
            <li>JavaScript</li>
            <li>Go</li>
            <li>C#</li>
            <li>C++</li>
            <li>Rust</li>
            <li>Solidity</li>
            <li>TypeScript</li>
            <li>Java</li>
        </ul>
        <div className='code-box'>{}
        <code>hello : "Cape Town ZA"</code><br/>
        <code>hello : "Cape Town ZA"</code><br/>
        <code>hello : "Cape Town ZA"</code>
        </div>
      <p className='code-comment'>//  Timed problems, real commit history, weekly projects you can point to</p>
    </div>
    </div>
  )
}
