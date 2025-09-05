package com.example.test;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

import butterknife.BindView;
import butterknife.OnClick;
import butterknife.ButterKnife;

import com.example.R;

public class TestActivity extends Activity {
    @BindView(R.id.textView)
    TextView textView;
    
    @OnClick(R.id.button)
    void onButtonClick() {
        // 点击事件
    }
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test);
        ButterKnife.bind(this);
    }
}
