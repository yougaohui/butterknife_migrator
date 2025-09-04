package com.example.test;

import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;

import butterknife.BindView;
import butterknife.OnClick;
import butterknife.ButterKnife;

public class MainActivity extends AppCompatActivity {
    
    @BindView(R.id.title_text)
    TextView titleText;
    
    @BindView(R.id.submit_button)
    Button submitButton;
    
    @BindView(R.id.cancel_button)
    Button cancelButton;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        
        // 绑定ButterKnife
        ButterKnife.bind(this);
        
        // 其他初始化代码
        titleText.setText("Hello World");
    }
    
    @OnClick({R.id.submit_button, R.id.cancel_button})
    public void onButtonClick(View view) {
        if (view.getId() == R.id.submit_button) {
            // 处理提交按钮点击
            titleText.setText("Submit clicked!");
        } else if (view.getId() == R.id.cancel_button) {
            // 处理取消按钮点击
            titleText.setText("Cancel clicked!");
        }
    }
    
    @OnClick(R.id.title_text)
    public void onTitleClick(View view) {
        // 处理标题点击
        titleText.setText("Title clicked!");
    }
}