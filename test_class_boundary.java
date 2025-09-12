package com.test;

import butterknife.BindView;
import butterknife.ButterKnife;
import butterknife.OnClick;

public class TestClass {
    @BindView(R.id.button1) Button button1;
    @BindView(R.id.button2) Button button2;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.test);
        ButterKnife.bind(this);
    }
    
    @OnClick(R.id.button1)
    public void onClick(View view) {
        // test
    }
    
    public class InnerClass {
        public void test() {
            // inner class
        }
    }
}