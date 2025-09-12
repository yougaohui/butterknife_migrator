package com.test;

import android.os.Bundle;
import android.widget.TextView;
import butterknife.BindView;
import butterknife.ButterKnife;

public class TestActivity {
    @BindView(R.id.textView) TextView textView;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_test);
        ButterKnife.bind(this);
    }
    
    public class InnerClass {
        public void doSomething() {
            // Inner class content
        }
    }
}
